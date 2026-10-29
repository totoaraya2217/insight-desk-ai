// Renderiza el subconjunto de Markdown que usa Gemini (párrafos, listas, **negrita**, # títulos)
// como elementos React. No usa innerHTML: el texto del modelo nunca se interpreta como HTML.

function enLinea(texto, clave) {
  return texto.split(/(\*\*[^*]+\*\*)/g).map((trozo, i) =>
    trozo.startsWith("**") && trozo.endsWith("**") ? <strong key={`${clave}-${i}`}>{trozo.slice(2, -2)}</strong> : trozo
  );
}

export default function TextoAgente({ texto }) {
  const bloques = [];
  let lista = null;

  texto.split("\n").forEach((linea, i) => {
    const item = linea.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)$/);
    if (item) {
      if (!lista) bloques.push((lista = { tipo: "lista", items: [] }));
      lista.items.push(enLinea(item[1], i));
      return;
    }
    lista = null;
    const titulo = linea.match(/^#{1,6}\s+(.*)$/);
    if (titulo) bloques.push({ tipo: "titulo", contenido: enLinea(titulo[1], i) });
    else if (linea.trim()) bloques.push({ tipo: "parrafo", contenido: enLinea(linea, i) });
  });

  return (
    <div className="texto-agente">
      {bloques.map((b, i) =>
        b.tipo === "lista" ? (
          <ul key={i}>{b.items.map((it, j) => <li key={j}>{it}</li>)}</ul>
        ) : b.tipo === "titulo" ? (
          <p key={i} className="strong">{b.contenido}</p>
        ) : (
          <p key={i}>{b.contenido}</p>
        )
      )}
    </div>
  );
}
