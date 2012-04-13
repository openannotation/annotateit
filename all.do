for f in annotateit/static/**/*.less; do
  echo "${f%.less}.css"
done | xargs redo-ifchange
redo-ifchange annotateit/static/annotation.embed.css