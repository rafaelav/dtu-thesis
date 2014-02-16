dir="../wifi_data"
for f in "$dir"/*; do
  b="_sorted"
  sort "$f" -o "$f"$b
done
