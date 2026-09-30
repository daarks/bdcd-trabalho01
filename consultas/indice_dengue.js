// Base 1 (dengue_br.alertas) - item (g): plano de consulta antes e depois do indice.

const base = db.getSiblingDB("dengue_br");
const NOME_INDICE = "geocode_1_data_iniSE_-1";

// Consulta alvo: as semanas de 2024 de um municipio especifico (Sao Paulo).
const filtro = {
  geocode: 3550308,
  data_iniSE: { $gte: ISODate("2024-01-01"), $lt: ISODate("2025-01-01") },
};

function resumo(rotulo) {
  const plano = base.alertas.find(filtro).explain("executionStats");
  const stats = plano.executionStats;
  console.log("--- " + rotulo + " ---");
  console.log("estagio vencedor        : " + JSON.stringify(plano.queryPlanner.winningPlan));
  console.log("documentos retornados   : " + stats.nReturned);
  console.log("documentos examinados   : " + stats.totalDocsExamined);
  console.log("chaves de indice lidas  : " + stats.totalKeysExamined);
  console.log("tempo de execucao (ms)  : " + stats.executionTimeMillis);
  console.log("");
}

// o script roda mais de uma vez, entao o indice anterior e removido para refazer a comparacao
if (base.alertas.getIndexes().some((i) => i.name === NOME_INDICE)) {
  base.alertas.dropIndex(NOME_INDICE);
}

console.log("Consulta: " + JSON.stringify(filtro));
console.log("Total de documentos na collection: " + base.alertas.countDocuments());
console.log("");

resumo("ANTES DA CRIACAO DO INDICE");

base.alertas.createIndex({ geocode: 1, data_iniSE: -1 });
console.log("Indice criado: " + NOME_INDICE);
console.log("");

resumo("DEPOIS DA CRIACAO DO INDICE");
