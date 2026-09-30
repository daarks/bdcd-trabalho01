// Base 2 (ibge.municipios + ibge.populacao) - duas consultas complexas, item (f) do enunciado.

const base = db.getSiblingDB("ibge");

function mostra(titulo, objetivo, resultado) {
  console.log("=".repeat(96));
  console.log(titulo);
  console.log("Objetivo: " + objetivo);
  console.log("=".repeat(96));
  resultado.forEach((doc) => console.log(JSON.stringify(doc)));
  console.log("");
}

// O join usa o geocode de 7 digitos, que no IBGE e o campo id do municipio.
const juntaPopulacao = [
  {
    $lookup: {
      from: "populacao",
      localField: "id",
      foreignField: "geocode",
      as: "dados_populacao",
    },
  },
  { $unwind: "$dados_populacao" },
];

const consulta1 = base.municipios
  .aggregate([
    ...juntaPopulacao,
    {
      $group: {
        _id: "$regiao-imediata.regiao-intermediaria.UF.sigla",
        regiao: { $first: "$regiao-imediata.regiao-intermediaria.UF.regiao.nome" },
        municipios: { $sum: 1 },
        populacao_total: { $sum: "$dados_populacao.populacao" },
        populacao_media: { $avg: "$dados_populacao.populacao" },
      },
    },
    {
      $project: {
        _id: 0,
        uf: "$_id",
        regiao: 1,
        municipios: 1,
        populacao_total: 1,
        populacao_media: { $round: ["$populacao_media", 0] },
      },
    },
    { $sort: { populacao_total: -1 } },
    { $limit: 10 },
  ])
  .toArray();

mostra(
  "CONSULTA 1 - Municipios e populacao por UF (join entre municipios e populacao)",
  "juntar a hierarquia territorial do IBGE com a estimativa populacional para ver, por " +
    "UF, quantos municipios existem, a populacao total e o porte medio do municipio.",
  consulta1
);

const consulta2 = base.municipios
  .aggregate([
    ...juntaPopulacao,
    {
      $group: {
        _id: "$regiao-imediata.regiao-intermediaria.UF.regiao.nome",
        populacao_regiao: { $sum: "$dados_populacao.populacao" },
        // $topN resolve o ranking dentro de cada grupo sem precisar de sort global
        mais_populosos: {
          $topN: {
            n: 3,
            sortBy: { "dados_populacao.populacao": -1 },
            output: {
              municipio: "$nome",
              uf: "$regiao-imediata.regiao-intermediaria.UF.sigla",
              populacao: "$dados_populacao.populacao",
            },
          },
        },
      },
    },
    { $project: { _id: 0, regiao: "$_id", populacao_regiao: 1, mais_populosos: 1 } },
    { $sort: { populacao_regiao: -1 } },
  ])
  .toArray();

mostra(
  "CONSULTA 2 - Os 3 municipios mais populosos de cada regiao",
  "mostrar a concentracao populacional dentro de cada regiao do pais, comparando os tres " +
    "maiores municipios com o total da regiao.",
  consulta2
);
