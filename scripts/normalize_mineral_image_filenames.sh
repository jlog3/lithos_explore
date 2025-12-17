cd frontend/public/textures
# cd frontend/public/textures/cover_variants
for dir in *; do
  if [ -d "$dir" ] && ! echo "$dir" | grep -q -E '^(archive|ground025|simple_quartz|Rocks002|Rocks011)$'; then
    cd "$dir"
    i=1
    for file in *; do
      if [ -f "$file" ]; then
        mv -v "$file" "${dir}${i}.jpg"
        ((i++))
      fi
    done
    cd ..
  fi
done
cd ../../..
