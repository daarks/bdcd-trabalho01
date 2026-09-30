// Base 1 (dengue_br.alertas) - duas consultas complexas, item (f) do enunciado.

const base = db.getSiblingDB("dengue_br");

function mostra(titulo, objetivo, resultado) {
  console.log("=".repeat(96));
  console.log(titulo);
  console.log("Objetivo: " + objetivo);
  console.log("=".repeat(96));
  resultado.forEach((doc) => console.log(JSON.stringify(doc)));
  console.log("");
}

// Consulta 1: as semanas epidemiologicas de 2024 vao de 202401 a 202453.
const consulta1 = base.alertas
  .aggregate([
    { $match: { SE: { $gte: 202401, $lte: 202453 } } },
    {
      $group: {
        _id: "$geocode",
        municipio: { $first: "$municipio_nome" },
        casos: { $sum: { $ifNull: ["$casos", 0] } },
        populacao: { $max: "$pop" },
        semanas_alerta_vermelho: {
          $sum: { $cond: [{ $eq: ["$nivel", 4] }, 1, 0] },
        },
      },
    },
    {
      $project: {
        _id: 0,
        municipio: 1,
        casos: 1,
        populacao: 1,
        // incidencia acumulada no ano, no padrao epidemiologico de casos por 100 mil habitantes
        incidencia_100mil: {
          $round: [
            { $multiply: [{ $divide: ["$casos", "$populacao"] }, 100000] },
            1,
          ],
        },
        semanas_alerta_vermelho: 1,
      },
    },
    { $sort: { casos: -1 } },
    { $limit: 10 },
  ])
  .toArray();

mostra(
  "CONSULTA 1 - Top 10 municipios por casos de dengue em 2024",
  "ranquear os municipios com mais casos notificados em 2024 e comparar o peso real " +
    "desses casos pela incidencia por 100 mil habitantes, junto do numero de semanas " +
    "em que o municipio ficou no nivel maximo de alerta.",
  consulta1
);

// Consulta 2: SE tem o formato AAAASS, entao ano e semana saem do mesmo campo.
const consulta2 = base.alertas
  .aggregate([
    {
      $addFields: {
        ano: { $toInt: { $substrBytes: [{ $toString: "$SE" }, 0, 4] } },
        semana: { $mod: ["$SE", 100] },
      },
    },
    { $match: { ano: { $gte: 2015, $lte: 2024 }, semana: { $lte: 52 } } },
    {
      $group: {
        _id: "$semana",
        casos_medios: { $avg: { $ifNull: ["$casos", 0] } },
        temperatura_media: { $avg: "$tempmed" },
        alertas_vermelhos: { $sum: { $cond: [{ $eq: ["$nivel", 4] }, 1, 0] } },
      },
    },
    {
      $project: {
        _id: 0,
        semana_epidemiologica: "$_id",
        casos_medios: { $round: ["$casos_medios", 1] },
        temperatura_media: { $round: ["$temperatura_media", 1] },
        alertas_vermelhos: 1,
      },
    },
    { $sort: { casos_medios: -1 } },
    { $limit: 10 },
  ])
  .toArray();

mostra(
  "CONSULTA 2 - As 10 semanas epidemiologicas mais criticas (media de 2015 a 2024)",
  "descobrir em que ponto do calendario a dengue pesa mais, cruzando a media de casos " +
    "por semana epidemiologica com a temperatura media registrada e a quantidade de " +
    "alertas no nivel vermelho.",
  consulta2
);
