"""Testes automatizados do pipeline de extração de sintomas cardiovasculares.

Cobre: negação (E1), extração temporal (E2), scoring declarativo (E3),
normalização (E4), robustez de regex (E5), fatores de risco e medicações (E6),
saída dual (E7), red flags (E8).

Uso:
    pytest tests/test_extracao.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cardio_extrator.extratores import (
    achados_presentes,
    extrair_contexto,
    extrair_fatores_risco,
    extrair_medicacoes,
    extrair_qualificadores,
    extrair_sintomas,
    extrair_temporal,
)
from cardio_extrator.inferencia import (
    avaliar_condicao,
    avaliar_red_flags,
    pontuar_doenca,
    pontuar_doencas,
)
from cardio_extrator.io import ARQUIVO_MAPA, carregar_mapa
from cardio_extrator.modelos import AchadoClinico, ResultadoAnalise
from cardio_extrator.negacao import _tokenizar, detectar_negacao
from cardio_extrator.pipeline import analisar_relato
from cardio_extrator.preprocessamento import normalizar


def _extrair(texto: str):
    """Helper: normaliza, tokeniza e extrai sintomas de uma vez."""
    texto_norm = normalizar(texto)
    tokens, posicoes = _tokenizar(texto_norm)
    return extrair_sintomas(texto_norm, tokens, posicoes)


def _extrair_quals(texto: str, presentes: set[str]):
    """Helper: normaliza e extrai qualificadores."""
    return extrair_qualificadores(normalizar(texto), presentes)


def _norm(fn, texto, *args):
    """Helper: normaliza texto e delega a qualquer extrator."""
    return fn(normalizar(texto), *args)


@pytest.fixture
def mapa():
    """Carrega o mapa de conhecimento real."""
    return carregar_mapa(ARQUIVO_MAPA)


# ---------------------------------------------------------------------------
# E1 — negação
# ---------------------------------------------------------------------------

class TestNegacao:
    """Testes do motor de negação contextual."""

    def test_negacao_simples(self):
        """'Não sinto dor no peito' → dor_toracica ausente."""
        achados = _extrair("Não sinto dor no peito")
        dor = [a for a in achados if a.sintoma == "dor_toracica"]
        assert len(dor) == 1
        assert dor[0].presente is False
        assert dor[0].negador == "não"

    def test_negacao_com_afirmacao(self):
        """'Nego dor no peito mas sinto falta de ar' → dor=False, dispneia=True."""
        achados = _extrair(
            "Nego dor no peito mas sinto falta de ar intensa"
        )
        sintomas = {a.sintoma: a.presente for a in achados}
        assert sintomas.get("dor_toracica") is False
        assert sintomas.get("dispneia") is True

    def test_dupla_negacao(self):
        """'Não posso negar que sinto um aperto no peito' → dor_toracica=True."""
        achados = _extrair(
            "Não posso negar que sinto um aperto no peito"
        )
        dor = [a for a in achados if a.sintoma == "dor_toracica"]
        assert len(dor) == 1
        assert dor[0].presente is True

    def test_negacao_com_sem(self):
        """'Sem queixas de tontura' → tontura ausente."""
        achados = _extrair("Sem queixas de tontura")
        tontura = [a for a in achados if a.sintoma == "tontura"]
        assert len(tontura) == 1
        assert tontura[0].presente is False

    def test_delimitador_escopo_conjuncao(self):
        """Negação não atravessa conjunção 'e'."""
        achados = _extrair(
            "Cansaço extremo que não melhora com repouso e falta de ar"
        )
        dispneia = [a for a in achados if a.sintoma == "dispneia"]
        assert len(dispneia) == 1
        assert dispneia[0].presente is True

    def test_delimitador_escopo_virgula(self):
        """Negação não atravessa vírgula."""
        achados = _extrair(
            "Não tenho náusea, mas sinto dor no peito"
        )
        dor = [a for a in achados if a.sintoma == "dor_toracica"]
        assert len(dor) == 1
        assert dor[0].presente is True


# ---------------------------------------------------------------------------
# E2 — extração temporal
# ---------------------------------------------------------------------------

class TestTemporal:
    """Testes da extração de atributos temporais."""

    def test_inicio_ha_dias(self):
        """'Dor no peito há 3 dias' → inicio='3 dias'."""
        temporal = _norm(extrair_temporal,"Dor no peito há 3 dias")
        assert "inicio" in temporal
        assert "3 dias" in temporal["inicio"]

    def test_inicio_ha_texto(self):
        """'Há duas semanas sinto falta de ar' → inicio contém 'semanas'."""
        temporal = _norm(extrair_temporal,"Há duas semanas sinto falta de ar")
        assert "inicio" in temporal
        assert "semanas" in temporal["inicio"]

    def test_duracao(self):
        """'Dor que dura vários minutos' → duracao contém 'minutos'."""
        temporal = _norm(extrair_temporal,
            "Batimentos irregulares que duram vários minutos"
        )
        assert "duracao" in temporal
        assert "minutos" in temporal["duracao"]

    def test_progressao_piorando(self):
        """'Falta de ar que vem piorando' → progressao='piorando'."""
        temporal = _norm(extrair_temporal,
            "Sinto falta de ar que vem piorando nas últimas semanas"
        )
        assert "progressao" in temporal
        assert "piorando" in temporal["progressao"]

    def test_frequencia(self):
        """'Toda noite acordo sem ar' → frequencia='toda noite'."""
        temporal = _norm(extrair_temporal,"Toda noite acordo sem ar")
        assert "frequencia" in temporal
        assert "toda noite" in temporal["frequencia"]


# ---------------------------------------------------------------------------
# E3 — scoring declarativo
# ---------------------------------------------------------------------------

class TestScoring:
    """Testes do motor de scoring declarativo."""

    def test_nova_doenca_sem_alterar_codigo(self, mapa):
        """Adicionar doença fictícia ao JSON e verificar que scoring funciona."""
        doenca_ficticia = {
            "nome_exibicao": "Doença Fictícia",
            "scoring": {
                "sintomas": {
                    "febre": {"peso_base": 1.0},
                    "fadiga": {"peso_base": 0.5},
                },
                "regras_bonificacao": [
                    {
                        "condicao": {"sintoma": "febre"},
                        "bonus": 0.5,
                        "justificativa": "Teste",
                    },
                ],
                "regras_exclusao": [],
                "fatores_risco": {},
            },
        }
        score, justificativas = pontuar_doenca(
            doenca_ficticia,
            sintomas_presentes={"febre", "fadiga"},
            qualificadores={},
            contexto={},
            fatores_risco={},
        )
        assert score == 2.0  # 1.0 + 0.5 + 0.5 (bônus)
        assert len(justificativas) == 3

    def test_normalizacao(self, mapa):
        """Score normalizado deve estar entre 0.0 e 1.0."""
        achados = _extrair(
            "Sinto dor forte no peito, falta de ar, tontura e desmaiei"
        )
        presentes = achados_presentes(achados)
        diagnosticos = pontuar_doencas(
            presentes, {}, {}, {}, mapa,
        )
        for diag in diagnosticos:
            assert 0.0 <= diag.score_normalizado <= 1.0

    def test_penalidade_aplicada(self, mapa):
        """Dor opressiva deve penalizar pericardite."""
        achados = _extrair("Sinto dor no peito como um aperto forte")
        presentes = achados_presentes(achados)
        qualificadores = _extrair_quals(
            "Sinto dor no peito como um aperto forte", presentes,
        )
        pericardite_cfg = mapa["pericardite"]
        score, justificativas = pontuar_doenca(
            pericardite_cfg, presentes, qualificadores, {}, {},
        )
        penalidades = [j for j in justificativas if "penalidade" in j]
        assert len(penalidades) > 0

    def test_avaliador_and(self):
        """Operador AND: todos os critérios devem ser verdadeiros."""
        cond = {
            "operador": "AND",
            "criterios": [
                {"sintoma": "dispneia"},
                {"sintoma": "edema_membros_inferiores"},
            ],
        }
        assert avaliar_condicao(
            cond, {"dispneia", "edema_membros_inferiores"}, {}, {}, {},
        ) is True
        assert avaliar_condicao(
            cond, {"dispneia"}, {}, {}, {},
        ) is False

    def test_avaliador_or(self):
        """Operador OR: ao menos um critério verdadeiro."""
        cond = {
            "operador": "OR",
            "criterios": [
                {"sintoma": "sudorese"},
                {"sintoma": "nausea"},
            ],
        }
        assert avaliar_condicao(
            cond, {"nausea"}, {}, {}, {},
        ) is True
        assert avaliar_condicao(
            cond, {"febre"}, {}, {}, {},
        ) is False

    def test_avaliador_count_ge(self):
        """Operador COUNT_GE: limiar mínimo de critérios verdadeiros."""
        cond = {
            "operador": "COUNT_GE",
            "criterios": [
                {"sintoma": "cefaleia"},
                {"sintoma": "tontura"},
                {"sintoma": "zumbido"},
                {"sintoma": "epistaxe"},
            ],
            "limiar": 3,
        }
        assert avaliar_condicao(
            cond, {"cefaleia", "tontura", "zumbido"}, {}, {}, {},
        ) is True
        assert avaliar_condicao(
            cond, {"cefaleia", "tontura"}, {}, {}, {},
        ) is False

    def test_avaliador_qualificador(self):
        """Avaliação de qualificador específico."""
        cond = {"qualificador": "dor_toracica.tipo_opressiva"}
        quals = {"dor_toracica": {"tipo_opressiva": True}}
        assert avaliar_condicao(cond, set(), quals, {}, {}) is True
        assert avaliar_condicao(cond, set(), {}, {}, {}) is False

    def test_avaliador_contexto(self):
        """Avaliação de contexto clínico."""
        cond = {"contexto": "prodomo_viral"}
        assert avaliar_condicao(
            cond, set(), {}, {"prodomo_viral": True}, {},
        ) is True
        assert avaliar_condicao(cond, set(), {}, {}, {}) is False

    def test_avaliador_fator_risco(self):
        """Avaliação de fator de risco."""
        cond = {"fator_risco": "tabagismo"}
        assert avaliar_condicao(
            cond, set(), {}, {}, {"tabagismo": True},
        ) is True

    def test_fatores_risco_no_scoring(self, mapa):
        """Fatores de risco devem incrementar o score quando presentes."""
        dac = mapa["doenca_arterial_coronariana"]
        score_sem, _ = pontuar_doenca(
            dac, {"dor_toracica"}, {}, {}, {},
        )
        score_com, justificativas = pontuar_doenca(
            dac, {"dor_toracica"}, {}, {}, {"tabagismo": True, "diabetes": True},
        )
        assert score_com > score_sem
        fatores = [j for j in justificativas if "fator de risco" in j]
        assert len(fatores) == 2


# ---------------------------------------------------------------------------
# E4 — normalização
# ---------------------------------------------------------------------------

class TestNormalizacao:
    """Testes da normalização de pontuação."""

    def test_confianca_baixa(self, mapa):
        """Score normalizado < 0.3 deve ter confiança 'baixa'."""
        achados = _extrair("Sinto uma leve fadiga")
        diagnosticos = pontuar_doencas(achados_presentes(achados), {}, {}, {}, mapa)
        baixas = [d for d in diagnosticos if d.confianca == "baixa"]
        for d in baixas:
            assert d.score_normalizado < 0.3

    def test_confianca_alta(self, mapa):
        """Score normalizado >= 0.6 deve ter confiança 'alta'."""
        texto = (
            "Há duas semanas meu coração começou a disparar do nada, "
            "com batimentos irregulares. Sinto tontura e fadiga."
        )
        achados = _extrair(texto)
        presentes = achados_presentes(achados)
        quals = _extrair_quals(texto, presentes)
        diagnosticos = pontuar_doencas(presentes, quals, {}, {}, mapa)
        fa = [d for d in diagnosticos if d.doenca == "fibrilacao_atrial"]
        assert len(fa) == 1
        assert fa[0].confianca == "alta"
        assert fa[0].score_normalizado >= 0.6


# ---------------------------------------------------------------------------
# E5 — robustez de regex / coloquialismos
# ---------------------------------------------------------------------------

class TestColoquialismo:
    """Testes de robustez para contrações e linguagem coloquial."""

    def test_contracoes_pro(self):
        """'Dor que vai pro braço' → irradiação MSE detectada."""
        achados = _extrair("Dor no peito que vai pro braço esquerdo")
        presentes = achados_presentes(achados)
        quals = _extrair_quals(
            "Dor no peito que vai pro braço esquerdo", presentes,
        )
        assert "dor_toracica" in presentes
        assert quals.get("dor_toracica", {}).get("irradiacao_mse") is True

    def test_contracoes_to(self):
        """'Tô sentindo dor forte no peito' → dor_toracica=True."""
        achados = _extrair("Tô sentindo uma dor forte no peito")
        presentes = achados_presentes(achados)
        assert "dor_toracica" in presentes

    def test_normalizacao_espacos(self):
        """Espaços múltiplos e tabs devem ser normalizados."""
        texto = "Sinto   uma  dor\tforte  no   peito"
        norm = normalizar(texto)
        assert "  " not in norm
        assert "\t" not in norm

    def test_correcao_ortografica(self):
        """Erros ortográficos comuns devem ser corrigidos."""
        norm = normalizar("Sinto dispineia e pressao alta")
        assert "dispneia" in norm
        assert "pressão" in norm

    def test_dor_com_palavras_intermediarias(self):
        """'Sinto um aperto forte no meio do peito' → dor_toracica."""
        achados = _extrair(
            "Sinto um aperto forte no meio do peito"
        )
        presentes = achados_presentes(achados)
        assert "dor_toracica" in presentes

    def test_dpn_madrugada(self):
        """'Acordo de madrugada sem conseguir respirar' → DPN detectada."""
        achados = _extrair(
            "Acordo de madrugada sem conseguir respirar direito"
        )
        presentes = achados_presentes(achados)
        assert "dispneia_paroxistica_noturna" in presentes


# ---------------------------------------------------------------------------
# E6 — fatores de risco e medicações
# ---------------------------------------------------------------------------

class TestFatoresRisco:
    """Testes da extração de fatores de risco cardiovascular."""

    def test_tabagismo(self):
        """Detecção de tabagismo."""
        fatores = _norm(extrair_fatores_risco,"Sou fumante há 20 anos")
        assert fatores.get("tabagismo") is True

    def test_diabetes(self):
        """Detecção de diabetes."""
        fatores = _norm(extrair_fatores_risco,"Tenho diabetes tipo 2")
        assert fatores.get("diabetes") is True

    def test_hipertensao(self):
        """Detecção de hipertensão."""
        fatores = _norm(extrair_fatores_risco,"Minha pressão é alta")
        assert fatores.get("hipertensao") is True

    def test_multiplos_fatores(self):
        """Detecção de múltiplos fatores simultâneos."""
        fatores = _norm(extrair_fatores_risco,
            "Sou fumante, tenho diabetes e colesterol alto"
        )
        assert fatores.get("tabagismo") is True
        assert fatores.get("diabetes") is True
        assert fatores.get("dislipidemia") is True

    def test_sem_fatores(self):
        """Relato sem fatores de risco deve retornar vazio."""
        fatores = _norm(extrair_fatores_risco,"Sinto dor no peito há dois dias")
        assert len(fatores) == 0


class TestMedicacoes:
    """Testes da extração de medicações."""

    def test_anti_hipertensivo(self):
        """Detecção de anti-hipertensivo."""
        meds = _norm(extrair_medicacoes,"Tomo losartana 50mg todo dia")
        assert "anti_hipertensivo" in meds
        assert any("losartana" in m for m in meds["anti_hipertensivo"])

    def test_estatina(self):
        """Detecção de estatina."""
        meds = _norm(extrair_medicacoes,"Uso atorvastatina para o colesterol")
        assert "estatina" in meds

    def test_multiplas_classes(self):
        """Detecção de múltiplas classes de medicação."""
        meds = _norm(extrair_medicacoes,
            "Tomo losartana, aspirina e sinvastatina"
        )
        assert "anti_hipertensivo" in meds
        assert "antiplaquetario" in meds
        assert "estatina" in meds

    def test_sem_medicacoes(self):
        """Relato sem medicações deve retornar vazio."""
        meds = _norm(extrair_medicacoes,"Sinto tontura e dor de cabeça")
        assert len(meds) == 0


# ---------------------------------------------------------------------------
# E7 — saída estruturada
# ---------------------------------------------------------------------------

class TestSaidaEstruturada:
    """Testes da saída dual texto/JSON."""

    def test_resultado_to_json(self, mapa):
        """ResultadoAnalise.to_json() deve retornar dicionário serializável."""
        resultado = analisar_relato(
            "Sinto dor forte no peito há três dias", mapa,
        )
        dados = resultado.to_json()
        assert isinstance(dados, dict)
        assert "relato_original" in dados
        assert "sintomas" in dados
        assert "diagnosticos" in dados
        serializado = json.dumps(dados, ensure_ascii=False)
        assert len(serializado) > 0

    def test_resultado_campos_completos(self, mapa):
        """Todos os campos do ResultadoAnalise devem estar presentes."""
        resultado = analisar_relato("Sinto falta de ar e palpitações", mapa)
        assert isinstance(resultado, ResultadoAnalise)
        assert resultado.relato_original == "Sinto falta de ar e palpitações"
        assert isinstance(resultado.sintomas, list)
        assert isinstance(resultado.qualificadores, dict)
        assert isinstance(resultado.contexto, dict)
        assert isinstance(resultado.temporal, dict)
        assert isinstance(resultado.fatores_risco, dict)
        assert isinstance(resultado.medicacoes, dict)
        assert isinstance(resultado.diagnosticos, list)
        assert isinstance(resultado.alertas, list)


# ---------------------------------------------------------------------------
# E8 — red flags
# ---------------------------------------------------------------------------

class TestRedFlags:
    """Testes de detecção de red flags clínicas."""

    def test_ic_descompensada(self, mapa):
        """Dispneia + edema + ortopneia deve disparar alerta de IC descompensada."""
        alertas = avaliar_red_flags(
            mapa,
            sintomas_presentes={"dispneia", "edema_membros_inferiores", "ortopneia"},
            qualificadores={},
            contexto={},
            fatores_risco={},
        )
        nomes = [a.nome for a in alertas]
        assert "IC descompensada" in nomes

    def test_sincope_esforco(self, mapa):
        """Síncope + esforço físico deve disparar alerta."""
        alertas = avaliar_red_flags(
            mapa,
            sintomas_presentes={"sincope"},
            qualificadores={},
            contexto={"esforco_fisico": True},
            fatores_risco={},
        )
        nomes = [a.nome for a in alertas]
        assert "Síncope de esforço" in nomes

    def test_sca_provavel(self, mapa):
        """Dor opressiva + dispneia deve disparar alerta de SCA."""
        alertas = avaliar_red_flags(
            mapa,
            sintomas_presentes={"dor_toracica", "dispneia"},
            qualificadores={"dor_toracica": {"tipo_opressiva": True}},
            contexto={},
            fatores_risco={},
        )
        nomes = [a.nome for a in alertas]
        assert "SCA provável" in nomes

    def test_sem_red_flags(self, mapa):
        """Relato brando não deve disparar alertas."""
        alertas = avaliar_red_flags(
            mapa,
            sintomas_presentes={"cefaleia", "tontura"},
            qualificadores={},
            contexto={},
            fatores_risco={},
        )
        assert len(alertas) == 0

    def test_prioridade_urgente(self, mapa):
        """Todas as red flags devem ter prioridade URGENTE."""
        alertas = avaliar_red_flags(
            mapa,
            sintomas_presentes={
                "dor_toracica", "dispneia", "edema_membros_inferiores",
                "ortopneia", "sincope",
            },
            qualificadores={"dor_toracica": {"tipo_opressiva": True}},
            contexto={"esforco_fisico": True},
            fatores_risco={},
        )
        for alerta in alertas:
            assert alerta.prioridade == "URGENTE"


# ---------------------------------------------------------------------------
# integração
# ---------------------------------------------------------------------------

class TestIntegracao:
    """Testes de integração do pipeline completo."""

    def test_pipeline_10_relatos(self, mapa):
        """Os 10 relatos originais devem produzir diagnósticos coerentes."""
        from cardio_extrator.io import ARQUIVO_RELATOS, carregar_relatos
        relatos = carregar_relatos(ARQUIVO_RELATOS)
        assert len(relatos) == 10

        esperados = [
            "doenca_arterial_coronariana",
            "insuficiencia_cardiaca",
            "fibrilacao_atrial",
            "estenose_aortica",
            "hipertensao_arterial_sistemica",
            "miocardite",
            "pericardite",
            "estenose_aortica",
            "insuficiencia_cardiaca",
            "fibrilacao_atrial",
        ]

        for i, (relato, esperado) in enumerate(zip(relatos, esperados)):
            resultado = analisar_relato(relato, mapa)
            assert len(resultado.diagnosticos) > 0, f"Relato {i+1} sem diagnósticos"
            assert resultado.diagnosticos[0].doenca == esperado, (
                f"Relato {i+1}: esperado {esperado}, "
                f"obteve {resultado.diagnosticos[0].doenca}"
            )

    def test_diagnostico_correto_dac(self, mapa):
        """Relato clássico de DAC deve ter DAC como primeiro diagnóstico."""
        resultado = analisar_relato(
            "Há três dias sinto uma dor forte no peito, como um aperto, "
            "que aparece quando subo escadas. A dor vai para o braço esquerdo "
            "e melhora quando paro para descansar.",
            mapa,
        )
        assert resultado.diagnosticos[0].doenca == "doenca_arterial_coronariana"
        assert resultado.diagnosticos[0].confianca in ("moderada", "alta")

    def test_diagnostico_correto_pericardite(self, mapa):
        """Relato clássico de pericardite deve ter pericardite como primeiro."""
        resultado = analisar_relato(
            "Sinto uma dor aguda no peito que piora quando respiro fundo. "
            "Melhora quando sento e inclino para frente. "
            "A dor irradia para o trapézio e tenho febre.",
            mapa,
        )
        assert resultado.diagnosticos[0].doenca == "pericardite"
        assert resultado.diagnosticos[0].confianca == "alta"
