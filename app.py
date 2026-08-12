from flask import Flask, Response
import pandas as pd
import requests
import json

app = Flask(__name__)

COMPANIES = {
    "bimp": {
        "realisasi": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-dan-rugi-bimp-20250701-20251231",
        "realisasi-harian": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-rugi-harian-bimp-20250701-20251231",
        "analitik": "https://dashboard.mahkotagroup.com/api/powerbi-feed/realisasi-bimp-20250701-20251231",
        "processing": "https://dashboard.mahkotagroup.com/api/powerbi-feed/processing-labour-bimp-20250701-20251231",
        "production": "https://dashboard.mahkotagroup.com/api/powerbi-feed/produksi-harian-bimp-20250701-20261231"
    },
    "bimr": {
        "realisasi": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-dan-rugi-bimr-20250701-20251231",
        "realisasi-harian": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-rugi-harian-bimr-20250701-20251231",
        "analitik": "https://dashboard.mahkotagroup.com/api/powerbi-feed/realisasi-bimr-20250701-20251231",
        "processing": "https://dashboard.mahkotagroup.com/api/powerbi-feed/processing-labour-bimr-20250701-20251231",
        "production": "https://dashboard.mahkotagroup.com/api/powerbi-feed/produksi-harian-bimr-20250701-20261231"
    },
    "bims": {
        "realisasi": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-dan-rugi-bims-20250701-20250930",
        "realisasi-harian": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-rugi-harian-bims-20250701-20250930",
        "analitik": "https://dashboard.mahkotagroup.com/api/powerbi-feed/realisasi-bims-20250701-20250930",
        "processing": "https://dashboard.mahkotagroup.com/api/powerbi-feed/processing-labour-bims-20250701-20250930",
        "production": "https://dashboard.mahkotagroup.com/api/powerbi-feed/produksi-harian-bims-20250701-20261231"
    },
    "mul": {
        "realisasi": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-dan-rugi-mul-20250701-20251231",
        "realisasi-harian": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-rugi-harian-mul-20250701-20251231",
        "analitik": "https://dashboard.mahkotagroup.com/api/powerbi-feed/realisasi-mul-20250701-20251231",
        "processing": "https://dashboard.mahkotagroup.com/api/powerbi-feed/processing-labour-mul-20250701-20251231",
        "production": "https://dashboard.mahkotagroup.com/api/powerbi-feed/produksi-harian-mul-20250701-20261231"
    },
    "kpnj": {
        "realisasi": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-dan-rugi-kpnj-20250701-20251231",
        "realisasi-harian": "https://dashboard.mahkotagroup.com/api/powerbi-feed/laba-rugi-harian-kpnj-20250701-20251231",
        "analitik": "https://dashboard.mahkotagroup.com/api/powerbi-feed/realisasi-kpnj-20250701-20251231",
        "processing": "https://dashboard.mahkotagroup.com/api/powerbi-feed/processing-labour-kpnj-20250701-20251231",
        "production": "https://dashboard.mahkotagroup.com/api/powerbi-feed/produksi-harian-kpnj-20250701-20261231"
    }
}

# Data Helper
def get_dataframe(url):
    response = requests.get(url)
    result = response.json()
    return pd.DataFrame(result["data"])

@app.route("/realisasi/<company>")
def get_data_realisasi(company):

    df = get_dataframe(COMPANIES[company]["realisasi"])

    # Balik tanda nominal untuk Pendapatan dan Pendapatan Lain-lain
    mask_pendapatan = df["Deskripsi"].isin(["Pendapatan", "Pendapatan Lain-lain"])
    df.loc[mask_pendapatan, "Realisasi Biaya"] = df.loc[mask_pendapatan, "Realisasi Biaya"] * -1

    # Bulatkan nilai 2 angka di belakang koma
    df["Realisasi Biaya"] = df["Realisasi Biaya"].round(2)

    # Susun kolom akhir
    final_cols = [
        "Tahun", "Bulan", "Overview", "Deskripsi", "No Akun", "Rincian Deskripsi", "Realisasi Biaya"
    ]

    df = df[final_cols].copy()
    records = df.to_dict(orient="records")

    return Response(
        json.dumps(records, ensure_ascii=False),
        mimetype="application/json"
    )
    
@app.route("/realisasi-harian/<company>")
def get_data_realisasi_harian(company):

    df = get_dataframe(COMPANIES[company]["realisasi-harian"])

    # Balik tanda nominal untuk Pendapatan dan Pendapatan Lain-lain
    mask_pendapatan = df["Deskripsi"].isin(["Pendapatan", "Pendapatan Lain-lain"])
    df.loc[mask_pendapatan, "Realisasi Biaya"] = df.loc[mask_pendapatan, "Realisasi Biaya"] * -1

    # Bulatkan nilai 2 angka di belakang koma
    df["Realisasi Biaya"] = df["Realisasi Biaya"].round(2)

    # Susun kolom akhir
    final_cols = [
        "Tanggal","Tahun", "Bulan", "Overview", "Deskripsi", "No Akun", "Rincian Deskripsi", "Realisasi Biaya"
    ]

    df = df[final_cols].copy()
    records = df.to_dict(orient="records")

    return Response(
        json.dumps(records, ensure_ascii=False),
        mimetype="application/json"
    )

@app.route("/realisasi-akun-analitik/<company>")
def get_data_akun_analitik(company):
    df = get_dataframe(COMPANIES[company]["analitik"])

    # Balik tanda nominal untuk Pendapatan dan Pendapatan Lain-lain
    mask_pendapatan = df["Deskripsi"].isin(["Pendapatan", "Pendapatan Lain-lain"])
    df.loc[mask_pendapatan, "Nominal"] = df.loc[mask_pendapatan, "Nominal"] * -1

    # Bulatkan nilai 2 angka di belakang koma
    df["Nominal"] = df["Nominal"].round(2)

     # format tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Tanggal"] = df["Tanggal"].dt.strftime("%d/%m/%Y")

    # Susun kolom akhir
    final_cols = [
        "Tanggal", "Tahun", "Bulan", "Overview", "Deskripsi", "No Akun", "Nama Akun", "No Akun Analitik",
        "Nama Akun Analitik", "Kode Induk Analitik", "Kode Detail Analitik", "Tipe Unit", "Nominal"
    ]

    df = df[final_cols].copy()

    records = df.to_dict(orient="records")

    return Response(
        json.dumps(records, ensure_ascii=False),
        mimetype="application/json"
    )

@app.route("/processing-labour/<company>")
def get_data_processing_labour(company):
    df = get_dataframe(COMPANIES[company]["processing"])

    # Bulatkan nilai 2 angka di belakang koma
    df["Realisasi Biaya"] = df["Realisasi Biaya"].round(2)

    # Susun kolom akhir
    final_cols = [
        "Tahun", "Bulan", "Overview", "Deskripsi", "Tipe", "No Akun", "Rincian Deskripsi", "Realisasi Biaya"
    ]

    df = df[final_cols].copy()

    df = df[~df["Rincian Deskripsi"].str.contains("Peny", case=False, na=False)]

    records = df.to_dict(orient="records")

    return Response(
        json.dumps(records, ensure_ascii=False),
        mimetype="application/json"
    )

@app.route("/production/<company>")
def get_data_production(company):
    df = get_dataframe(COMPANIES[company]["production"])

    # format tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Tanggal"] = df["Tanggal"].dt.strftime("%d/%m/%Y")

    # format Total Jam Operasi
    df["Total Jam Operasi"] = (
        df["Total Jam Operasi"]
        .astype(float)
        .round(2)
        .astype(str)
        .str.rstrip("0")
        .str.rstrip(".")
    )

    records = df.to_dict(orient="records")

    return Response(
        json.dumps(records, ensure_ascii=False),
        mimetype="application/json"
    )

if __name__ == "__main__":
    app.run(debug=True)