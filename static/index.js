function formatNumber(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    const num = Number(value);
    if (isNaN(num)) return String(value);
    
    return num.toLocaleString('id-ID');
}


function convertDate(date) {

    return date.replace(/-/g, "");

}


async function getData() {

    const company =
        document.getElementById(
            "company"
        ).value;

    const report =
        document.getElementById(
            "report"
        ).value;

    const startDate =
        document.getElementById(
            "startDate"
        ).value;

    const endDate =
        document.getElementById(
            "endDate"
        ).value;

    const button =
        document.getElementById(
            "checkButton"
        );

    const loading =
        document.getElementById(
            "loading"
        );

    const status =
        document.getElementById(
            "status"
        );

    const result =
        document.getElementById(
            "result"
        );


    // -----------------------------------------
    // Validation
    // -----------------------------------------

    if (!startDate || !endDate) {

        showError(
            "Tanggal mulai dan tanggal akhir wajib diisi."
        );

        return;
    }


    if (startDate > endDate) {

        showError(
            "Tanggal mulai tidak boleh lebih besar dari tanggal akhir."
        );

        return;
    }


    // -----------------------------------------
    // Loading
    // -----------------------------------------

    button.disabled = true;

    loading.style.display = "inline";

    status.className = "status";

    result.style.display = "none";


    try {

        const start =
            convertDate(startDate);

        const end =
            convertDate(endDate);


        const url =
            `/api/totals/${report}/${company}` +
            `?start_date=${start}` +
            `&end_date=${end}`;


        const response =
            await fetch(url);

        let data;
        const text = await response.text();
        try {
            data = text ? JSON.parse(text) : {};
        } catch { data = {}; }

        if (!response.ok || !data.success) {

            throw new Error(
                (data &&data.error) ||
                text ||
                "Gagal mengambil data."
            );

        }


        // -------------------------------------
        // Display result
        // -------------------------------------

        document.getElementById(
            "sourceTotal"
        ).textContent =
            formatNumber(
                data.sourceTotal
            );


        document.getElementById(
            "finalTotal"
        ).textContent =
            formatNumber(
                data.finalTotal
            );


        document.getElementById(
            "difference"
        ).textContent =
            formatNumber(
                data.difference
            );


        document.getElementById(
            "percentage"
        ).textContent =
            data.finalPercentage +
            "%";


        document.getElementById(
            "resultCompany"
        ).textContent =
            data.companyName;


        document.getElementById(
            "resultReport"
        ).textContent =
            data.reportName;


        document.getElementById(
            "resultPeriod"
        ).textContent =
            `${startDate} s/d ${endDate}`;


        document.getElementById(
            "resultTotal"
        ).textContent =
            formatNumber(
                data.total
            );


        document.getElementById(
            "sourceUrl"
        ).textContent =
            data.sourceUrl;


        result.style.display = "block";


        showSuccess(
            "Data berhasil diambil."
        );

        await insertSearchHistory();

    }

    catch (error) {

        showError(
            error.message
        );

    }

    finally {

        button.disabled = false;

        loading.style.display = "none";

    }

}


function showSuccess(message) {

    const status =
        document.getElementById(
            "status"
        );

    status.textContent =
        message;

    status.className =
        "status success";

}


function showError(message) {

    const status =
        document.getElementById(
            "status"
        );

    status.textContent =
        message;

    status.className =
        "status error";

}

async function insertSearchHistory() {
    const data = {
        company: document.getElementById("company").value,
        report: document.getElementById("report").value,
        startDate: document.getElementById("startDate").value,
        endDate: document.getElementById("endDate").value,
        sourceTotal: document.getElementById("sourceTotal").textContent,
        finalTotal: document.getElementById("finalTotal").textContent
    };

    await fetch("/api/history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
}

function viewHistory() {
    fetch("/api/history")
        .then(res => res.json())
        .then(data => {
            // expect data to be an array of history rows
            const el = document.getElementById("historyData");
            if (!Array.isArray(data)) {
                el.textContent = "No history or unexpected response.";
                return;
            }
            // simple render: join JSON lines
            el.textContent = data.map(r => JSON.stringify(r)).join("\n");
        })
        .catch(err => {
            console.error(err);
            const el = document.getElementById("historyData");
            if (el) el.textContent = "Failed to load history.";
        });
}