// Item (e) do enunciado: listagem das collections criadas em cada base.

const bases = ["dengue_br", "ibge"];

for (const nome of bases) {
  const base = db.getSiblingDB(nome);
  console.log("Base: " + nome);
  const colecoes = base.getCollectionNames();
  for (const colecao of colecoes) {
    console.log("  " + colecao + " -> " + base[colecao].countDocuments() + " documentos");
  }
  console.log("");
}
