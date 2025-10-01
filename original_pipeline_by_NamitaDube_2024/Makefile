# original_pipeline_by_NamitaDube_2024/Makefile
PY?=python

# ---- USER EDITS: point these to your inputs ----
LGA_ROOT?=path/to/LGA_outputs
GLDDT_ROOT?=path/to/GlobalLDDT_logs
LOCAL_GDT_ROOT?=path/to/local_gdt_tables
LOCAL_LDDT_ROOT?=path/to/local_lddt_tables
# Optional residue window (comment out to use whole chain)
START?=
END?=
# ------------------------------------------------

all: composite plots

extract:
	$(PY) scripts/extract_global_gdt_rms.py --root $(LGA_ROOT) --out global_gdt_rms.csv
	$(PY) scripts/extract_global_lddt.py    --root $(GLDDT_ROOT) --out global_lddt.csv
	@if [ -n "$(START)" ] && [ -n "$(END)" ]; then \
		$(PY) scripts/extract_local_gdt.py   --root $(LOCAL_GDT_ROOT)  --out local_gdt.csv --start $(START) --end $(END); \
		$(PY) scripts/extract_local_lddt.py  --root $(LOCAL_LDDT_ROOT) --out local_lddt.csv --start $(START) --end $(END); \
	else \
		$(PY) scripts/extract_local_gdt.py   --root $(LOCAL_GDT_ROOT)  --out local_gdt.csv; \
		$(PY) scripts/extract_local_lddt.py  --root $(LOCAL_LDDT_ROOT) --out local_lddt.csv; \
	fi

merge: extract
	$(PY) scripts/merge_all.py \
	  --gdt_rms global_gdt_rms.csv \
	  --glddt   global_lddt.csv \
	  --local_gdt  local_gdt.csv \
	  --local_lddt local_lddt.csv \
	  --out combined_results.csv

normalize: merge
	$(PY) scripts/normalize_metrics.py --in combined_results.csv --out normalized_metrics.csv

composite: normalize
	$(PY) scripts/compositescores.py --in normalized_metrics.csv --out composite_scores.csv --gdt-cutoff 80 --lddt-cutoff 80

plots: composite
	$(PY) scripts/plot_models_bar.py     --csv composite_scores.csv --score CS4 --out models_vs_CS4.png
	$(PY) scripts/plot_best_per_group.py --csv composite_scores.csv --score CS4 --out best_per_group_CS4.png
	$(PY) scripts/plot_scatter_diagnostic.py --normalized normalized_metrics.csv --scores composite_scores.csv \
	    --x Global_GDT_normalized --y CS4 --out scatter_GGDT_vs_CS4.png

clean:
	rm -f global_gdt_rms.csv global_lddt.csv local_gdt.csv local_lddt.csv \
	      combined_results.csv normalized_metrics.csv composite_scores.csv \
	      models_vs_CS4.png best_per_group_CS4.png scatter_GGDT_vs_CS4.png
