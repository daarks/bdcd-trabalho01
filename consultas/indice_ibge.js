// Base 2 (ibge) - item (g): plano de consulta antes e depois do indice.

const base = db.getSiblingDB("ibge");
const NOME_INDICE = "geocode_1";

// Consulta alvo: o mesmo join da Consulta 1, que resolve o geocode em ibge.populacao.
const consulta = [
  {
    $lookup: {
      from: "populacao",
      localField: "id",
      foreignField: "geocode",
      as: "dados_populacao",
    },
  },
  { $unwind: "$dados_populacao" },
  {
    $group: {
      _id: "$regiao-imediata.regiao-intermediaria.UF.sigla",
      municipios: { $sum: 1 },
      populacao_total: { $sum: "$dados_populacao.populacao" },
    },
  },
];

function resumo(rotulo) {
  const plano = base.municipios.explain("executionStats").aggregate(consulta);
  const lookup = plano.stages.find((estagio) => estagio.$lookup);
  console.log("--- " + rotulo + " ---");
  console.log("estagio                 : $lookup em ibge.populacao");
  console.log("indices usados          : " + JSON.stringify(lookup.indexesUsed));
  console.log("varreduras de collection: " + Number(lookup.collectionScans));
  console.log("documentos examinados   : " + Number(lookup.totalDocsExamined));
  console.log("chaves de indice lidas  : " + Number(lookup.totalKeysExamined));
  console.log("documentos retornados   : " + Number(lookup.nReturned));
  console.log("tempo estimado (ms)     : " + Number(lookup.executionTimeMillisEstimate));
  console.log("");
}

// o script roda mais de uma vez, entao o indice anterior e removido para refazer a comparacao
if (base.populacao.getIndexes().some((i) => i.name === NOME_INDICE)) {
  base.populacao.dropIndex(NOME_INDICE);
}

console.log("Consulta: join de ibge.municipios (id) com ibge.populacao (geocode), agrupado por UF");
console.log(
  "Documentos: municipios=" +
    base.municipios.countDocuments() +
    " populacao=" +
    base.populacao.countDocuments()
);
console.log("");

resumo("ANTES DA CRIACAO DO INDICE");

base.populacao.createIndex({ geocode: 1 });
console.log("Indice criado: ibge.populacao." + NOME_INDICE);
console.log("");

resumo("DEPOIS DA CRIACAO DO INDICE");
