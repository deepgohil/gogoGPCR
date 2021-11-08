import pandas as pd
from pathlib import Path
import hail as hl
from typing import List

def get_position(gene: str, mapping: pd.DataFrame):
    
    blocks = mapping.loc[gene, "VCF_block"].split(",")
    chromosome = mapping.loc[gene, "GRCh38_region"]
    start = mapping.loc[gene, "GRCh38_start"]
    end = mapping.loc[gene, "GRCh38_end"]

    return chromosome, blocks, start, end

def lookup_regions(gene: str, mapping: pd.DataFrame):
    chromosome, _, start, end = get_position(gene, mapping)
    

    region = [
            hl.parse_locus_interval(
                f"[chr{chromosome}:{start}-chr{chromosome}:{end}]"
            )
        ]
    
    return region


def lookup_vcfs(mapping: pd.DataFrame, vcfdir: str, gene: str, version: str) -> list:
    
    chromosome, blocks, _, _ = get_position(gene, mapping)
    
    vcf_files = [
        f"file://{vcfdir}/ukb23156_c{chromosome}_b{block}_{version}.vcf.gz"
        for block in blocks
    ]

    return vcf_files

def are_variants_present(mt: hl.MatrixTable, var_col: str, variants: List[str]) -> None:
    for v in variants:    
        print(f"{v}: {mt.aggregate_rows(hl.agg.any(mt[var_col] == v))}")
        
def show_stats(mt):
    intr = mt.filter_rows((hl.is_defined(mt.annotations)))
    intr = hl.variant_qc(intr)
    intr = intr.rows() #intr = intr.select_rows(intr.variant_qc, intr.protCons, intr.annotations, intr.annotation).rows()
    #intr = intr.annotate(**intr.variant_qc)
    #intr = intr.annotate(**intr.annotations)
    #intr = intr.drop("variant_qc", "gq_stats", "dp_stats", "annotations")
    stats = intr.group_by(intr.annotation).aggregate(n_carriers = hl.agg.sum(intr.variant_qc.n_het),
                                                    n_variants = hl.agg.count())
    stats.show(-1)

