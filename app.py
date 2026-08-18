from flask import Flask, Response, render_template, request
import pandas as pd
import requests
import json
from datetime import datetime

app = Flask(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://dashboard.mahkotagroup.com/api/powerbi-feed"

COMPANIES = {
    "bimp": {
        "name": "BIMP"
    },
    "bimr": {
        "name": "BIMR"
    },
    "bims": {
        "name": "BIMS"
    },
    "mul": {
        "name": "MUL"
    },
    "kpnj": {
        "name": "KPNJ"
    }
}

REPORTS = {
    "realisasi": {
        "name": "Laba dan Rugi",
        "endpoint": "laba-dan-rugi-{company}-{start_date}-{end_date}"
    },
    "realisasi-harian": {
        "name": "Laba Rugi Harian",
        "endpoint": "laba-rugi-harian-{company}-{start_date}-{end_date}"
    },
    "analitik": {
        "name": "Realisasi Akun Analitik",
        "endpoint": "realisasi-{company}-{start_date}-{end_date}"
    },
    "processing": {
        "name": "Processing Labour",
        "endpoint": "processing-labour-{company}-{start_date}-{end_date}"
    },
    "production": {
        "name": "Production",
        "endpoint": "produksi-harian-{company}-{start_date}-{end_date}"
    }
}


# ============================================================
# HELPER
# ============================================================

def validate_date(date_string):
    """
    Validasi format tanggal YYYYMMDD.
    """

    try:
        datetime.strptime(date_string, "%Y%m%d")
        return True

    except ValueError:
        return False


def convert_date(date_string):
    """
    Mengubah tanggal HTML YYYY-MM-DD
    menjadi YYYYMMDD untuk endpoint API.
    """

    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj.strftime("%Y%m%d")

    except ValueError:
        return None


def build_api_url(company, report, start_date, end_date):
    """
    Membentuk URL API berdasarkan:
    company
    report
    start_date
    end_date
    """

    if company not in COMPANIES:
        raise ValueError(
            f"Company '{company}' tidak ditemukan"
        )

    if report not in REPORTS:
        raise ValueError(
            f"Report '{report}' tidak ditemukan"
        )

    endpoint_template = REPORTS[report]["endpoint"]

    endpoint = endpoint_template.format(
        company=company,
        start_date=start_date,
        end_date=end_date
    )

    return f"{BASE_URL}/{endpoint}"


def get_api_result(url):
    """
    Request ke API sumber.
    """

    response = requests.get(
        url,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


def get_dataframe(url):
    """
    Mengambil data API dan mengubahnya
    menjadi pandas DataFrame.
    """

    result = get_api_result(url)

    return pd.DataFrame(
        result.get("data", [])
    )


def json_response(data, status=200):
    """
    Helper response JSON.
    """

    return Response(
        json.dumps(
            data,
            ensure_ascii=False
        ),
        status=status,
        mimetype="application/json"
    )


# ============================================================
# HOME / HTML
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        companies=COMPANIES,
        reports=REPORTS
    )


# ============================================================
# TOTALS API
# ============================================================

@app.route("/api/totals/<report>/<company>")
def get_totals(report, company):

    start_date = request.args.get(
        "start_date"
    )

    end_date = request.args.get(
        "end_date"
    )

    # --------------------------------------------------------
    # Validasi company
    # --------------------------------------------------------

    if company not in COMPANIES:

        return json_response(
            {
                "success": False,
                "error": f"Company '{company}' tidak ditemukan"
            },
            404
        )

    # --------------------------------------------------------
    # Validasi report
    # --------------------------------------------------------

    if report not in REPORTS:

        return json_response(
            {
                "success": False,
                "error": f"Report '{report}' tidak ditemukan"
            },
            404
        )

    # --------------------------------------------------------
    # Validasi tanggal
    # --------------------------------------------------------

    if not start_date or not end_date:

        return json_response(
            {
                "success": False,
                "error": "start_date dan end_date wajib diisi"
            },
            400
        )

    if not validate_date(start_date):

        return json_response(
            {
                "success": False,
                "error": "start_date harus format YYYYMMDD"
            },
            400
        )

    if not validate_date(end_date):

        return json_response(
            {
                "success": False,
                "error": "end_date harus format YYYYMMDD"
            },
            400
        )

    # --------------------------------------------------------
    # Validasi periode
    # --------------------------------------------------------

    if start_date > end_date:

        return json_response(
            {
                "success": False,
                "error": "Tanggal mulai tidak boleh lebih besar dari tanggal akhir"
            },
            400
        )

    # --------------------------------------------------------
    # Build URL
    # --------------------------------------------------------

    try:

        url = build_api_url(
            company,
            report,
            start_date,
            end_date
        )

        # ----------------------------------------------------
        # Request API
        # ----------------------------------------------------

        result = get_api_result(url)

        source_total = result.get(
            "sourceTotal"
        ) or 0

        final_total = result.get(
            "finalTotal"
        ) or 0

        total = result.get(
            "total"
        )

        # ----------------------------------------------------
        # Calculation
        # ----------------------------------------------------

        difference = (
            source_total - final_total
        )

        if source_total:

            final_percentage = (
                final_total /
                source_total *
                100
            )

        else:

            final_percentage = 0

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        response = {

            "success": True,

            "company": company,

            "companyName":
                COMPANIES[company]["name"],

            "report": report,

            "reportName":
                REPORTS[report]["name"],

            "startDate": start_date,

            "endDate": end_date,

            "total": total,

            "sourceTotal": source_total,

            "finalTotal": final_total,

            "difference": difference,

            "finalPercentage":
                round(
                    final_percentage,
                    2
                ),

            "sourceUrl": url
        }

        return json_response(
            response
        )

    except requests.RequestException as e:

        return json_response(
            {
                "success": False,
                "error": "Gagal mengakses API sumber",
                "detail": str(e)
            },
            502
        )

    except Exception as e:

        return json_response(
            {
                "success": False,
                "error": "Terjadi kesalahan",
                "detail": str(e)
            },
            500
        )


# ============================================================
# REALISASI
# ============================================================

@app.route("/realisasi/<company>")
def get_data_realisasi(company):

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:

        return json_response(
            {
                "error":
                    "start_date dan end_date wajib diisi"
            },
            400
        )

    url = build_api_url(
        company,
        "realisasi",
        start_date,
        end_date
    )

    df = get_dataframe(url)

    # Balik tanda nominal
    mask_pendapatan = df["Deskripsi"].isin(
        [
            "Pendapatan",
            "Pendapatan Lain-lain"
        ]
    )

    df.loc[
        mask_pendapatan,
        "Realisasi Biaya"
    ] *= -1

    # Round
    df["Realisasi Biaya"] = (
        df["Realisasi Biaya"]
        .round(2)
    )

    final_cols = [
        "Tahun",
        "Bulan",
        "Overview",
        "Deskripsi",
        "No Akun",
        "Rincian Deskripsi",
        "Realisasi Biaya"
    ]

    df = df[final_cols].copy()

    return json_response(
        df.to_dict(
            orient="records"
        )
    )


# ============================================================
# REALISASI HARIAN
# ============================================================

@app.route("/realisasi-harian/<company>")
def get_data_realisasi_harian(company):

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:

        return json_response(
            {
                "error":
                    "start_date dan end_date wajib diisi"
            },
            400
        )

    url = build_api_url(
        company,
        "realisasi-harian",
        start_date,
        end_date
    )

    df = get_dataframe(url)

    mask_pendapatan = df["Deskripsi"].isin(
        [
            "Pendapatan",
            "Pendapatan Lain-lain"
        ]
    )

    df.loc[
        mask_pendapatan,
        "Realisasi Biaya"
    ] *= -1

    df["Realisasi Biaya"] = (
        df["Realisasi Biaya"]
        .round(2)
    )

    final_cols = [
        "Tanggal",
        "Tahun",
        "Bulan",
        "Overview",
        "Deskripsi",
        "No Akun",
        "Rincian Deskripsi",
        "Realisasi Biaya"
    ]

    df = df[final_cols].copy()

    return json_response(
        df.to_dict(
            orient="records"
        )
    )


# ============================================================
# ANALITIK
# ============================================================

@app.route("/realisasi-akun-analitik/<company>")
def get_data_akun_analitik(company):

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:

        return json_response(
            {
                "error":
                    "start_date dan end_date wajib diisi"
            },
            400
        )

    url = build_api_url(
        company,
        "analitik",
        start_date,
        end_date
    )

    df = get_dataframe(url)

    mask_pendapatan = df["Deskripsi"].isin(
        [
            "Pendapatan",
            "Pendapatan Lain-lain"
        ]
    )

    df.loc[
        mask_pendapatan,
        "Nominal"
    ] *= -1

    df["Nominal"] = (
        df["Nominal"]
        .round(2)
    )

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"]
    )

    df["Tanggal"] = (
        df["Tanggal"]
        .dt.strftime("%d/%m/%Y")
    )

    final_cols = [
        "Tanggal",
        "Tahun",
        "Bulan",
        "Overview",
        "Deskripsi",
        "No Akun",
        "Nama Akun",
        "No Akun Analitik",
        "Nama Akun Analitik",
        "Kode Induk Analitik",
        "Kode Detail Analitik",
        "Tipe Unit",
        "Nominal"
    ]

    df = df[final_cols].copy()

    return json_response(
        df.to_dict(
            orient="records"
        )
    )


# ============================================================
# PROCESSING LABOUR
# ============================================================

@app.route("/processing-labour/<company>")
def get_data_processing_labour(company):

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:

        return json_response(
            {
                "error":
                    "start_date dan end_date wajib diisi"
            },
            400
        )

    url = build_api_url(
        company,
        "processing",
        start_date,
        end_date
    )

    df = get_dataframe(url)

    df["Realisasi Biaya"] = (
        df["Realisasi Biaya"]
        .round(2)
    )

    final_cols = [
        "Tahun",
        "Bulan",
        "Overview",
        "Deskripsi",
        "Tipe",
        "No Akun",
        "Rincian Deskripsi",
        "Realisasi Biaya"
    ]

    df = df[final_cols].copy()

    df = df[
        ~df["Rincian Deskripsi"]
        .str.contains(
            "Peny",
            case=False,
            na=False
        )
    ]

    return json_response(
        df.to_dict(
            orient="records"
        )
    )


# ============================================================
# PRODUCTION
# ============================================================

@app.route("/production/<company>")
def get_data_production(company):

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:

        return json_response(
            {
                "error":
                    "start_date dan end_date wajib diisi"
            },
            400
        )

    url = build_api_url(
        company,
        "production",
        start_date,
        end_date
    )

    df = get_dataframe(url)

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"]
    )

    df["Tanggal"] = (
        df["Tanggal"]
        .dt.strftime("%d/%m/%Y")
    )

    df["Total Jam Operasi"] = (
        df["Total Jam Operasi"]
        .astype(float)
        .round(2)
        .astype(str)
        .str.rstrip("0")
        .str.rstrip(".")
    )

    return json_response(
        df.to_dict(
            orient="records"
        )
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8502,
        debug=True
    )