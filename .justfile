add $name:
	@uv run scripts/gen_typ.py "{{name}}"
	@typst compile --root . "typs/{{name}}.typ" "pdfs/{{name}}.pdf"
	@magick -density 300 "pdfs/{{name}}.pdf" -resize x1080 -background white -alpha remove -quality 90 "jpgs/{{name}}_p%02d.jpg"
	@python scripts/gen_typ.py "{{name}}" --cleanup --cleanup-images

add-la $name:
	@uv run scripts/gen_typ.py "{{name}}" --font "MonaspiceNe NFM"
	@typst compile --root . "typs/{{name}}.typ" "pdfs/{{name}}.pdf"
	@magick -density 300 "pdfs/{{name}}.pdf" -resize x1080 -background white -alpha remove -quality 90 "jpgs/{{name}}_p%02d.jpg"
	@python scripts/gen_typ.py "{{name}}" --cleanup --cleanup-images

add-zh $name:
	@uv run scripts/gen_typ.py "{{name}}" --font "Sarasa Mono SC"
	@typst compile --root . "typs/{{name}}.typ" "pdfs/{{name}}.pdf"
	@magick -density 300 "pdfs/{{name}}.pdf" -resize x1080 -background white -alpha remove -quality 90 "jpgs/{{name}}_p%02d.jpg"
	@python scripts/gen_typ.py "{{name}}" --cleanup --cleanup-images