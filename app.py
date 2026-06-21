from flask import Flask, render_template, request, redirect, send_from_directory
import pandas as pd

app = Flask(__name__)

df = pd.read_csv("devices.csv")


@app.route("/", methods=["GET", "POST"])
def home():

    results = None
    device_info = None
    master_df = pd.read_csv("devices_master.csv")

    phone_devices = (
        master_df[master_df["category"] == "Phones"]
        .sort_values(
            by="npu_tops",
            ascending=False
        )
        .head(2)
    )

    pc_devices = (
        master_df[master_df["category"] == "AI PCs"]
        .sort_values(
            by="npu_tops",
            ascending=False
        )
        .head(2)
    )

    tablet_devices = (
        master_df[master_df["category"] == "Tablets"]
        .sort_values(
            by="npu_tops",
            ascending=False
        )
        .head(2)
    )

    popular_comparisons = []

    if len(phone_devices) >= 2:
        popular_comparisons.append({
            "device1": phone_devices.iloc[0]["device"],
            "device2": phone_devices.iloc[1]["device"]
        })

    if len(pc_devices) >= 2:
        popular_comparisons.append({
            "device1": pc_devices.iloc[0]["device"],
            "device2": pc_devices.iloc[1]["device"]
        })

    if len(tablet_devices) >= 2:
        popular_comparisons.append({
            "device1": tablet_devices.iloc[0]["device"],
            "device2": tablet_devices.iloc[1]["device"]
        })

    if request.method == "POST":

        device_name = request.form["device"]

        results = df[
            df["device"].str.contains(
                device_name,
                case=False,
                na=False
            )
        ]

        if not results.empty:

            device = results.iloc[0]["device"]
            chipset = results.iloc[0]["chipset"]
            platform = results.iloc[0]["platform"]
            tops = int(results.iloc[0]["npu_tops"])
            min_os = results.iloc[0]["min_os"]

            local_count = len(
                results[
                    results["execution"] == "Local"
                ]
            )

            hybrid_count = len(
                results[
                    results["execution"] == "Hybrid"
                ]
            )

            if tops >= 45:
                readiness_score = 90
            elif tops >= 35:
                readiness_score = 80
            elif tops >= 25:
                readiness_score = 70
            else:
                readiness_score = 60

            if readiness_score >= 85:
                readiness = "Excellent"
            elif readiness_score >= 75:
                readiness = "Very Good"
            elif readiness_score >= 65:
                readiness = "Good"
            else:
                readiness = "Basic"

            if platform == "Gemini Nano":
                local_ai = "High"

            elif platform == "Copilot+":
                local_ai = "High"

            elif platform == "Apple Intelligence":
                local_ai = "Moderate"

            elif platform == "Galaxy AI":
                local_ai = "Moderate"

            else:
                local_ai = "Unknown"

            analysis = ""

            if platform == "Apple Intelligence":
                analysis = (
                    "Apple Intelligence uses a hybrid architecture. "
                    "Many requests run locally on the Apple Neural Engine, "
                    "while more complex tasks may use Apple's Private Cloud Compute."
                )

            elif platform == "Gemini Nano":
                analysis = (
                    "Gemini Nano is primarily designed for on-device AI. "
                    "Many supported features execute locally without requiring cloud processing."
                )

            elif platform == "Galaxy AI":
                analysis = (
                    "Galaxy AI combines local NPU acceleration with cloud services. "
                    "Some features run locally while others rely on Samsung cloud infrastructure."
                )

            elif platform == "Copilot+":
                analysis = (
                    "Copilot+ PCs are designed around local AI workloads. "
                    "The NPU accelerates many AI tasks directly on-device while some advanced services remain cloud-assisted."
                )

            device_info = {
                "device": device,
                "chipset": chipset,
                "platform": platform,
                "npu_tops": tops,
                "min_os": min_os,
                "readiness": readiness,
                "readiness_score": readiness_score,
                "local_features": local_count,
                "hybrid_features": hybrid_count,
                "local_ai": local_ai,
                "analysis": analysis,

            }

    return render_template(
        "index.html",
        results=results,
        device_info=device_info,
        popular_comparisons=popular_comparisons
    )

def get_local_ai(platform):
    if platform == "Gemini Nano":
        return "High"
    elif platform == "Copilot+":
        return "High"
    elif platform == "Apple Intelligence":
        return "Moderate"
    elif platform == "Galaxy AI":
        return "Moderate"
    return "Unknown"


def get_best_for(platform):
    if platform == "Gemini Nano":
        return "Offline AI"

    elif platform == "Galaxy AI":
        return "AI Productivity"

    elif platform == "Apple Intelligence":
        return "Privacy Focused AI"

    elif platform == "Copilot+":
        return "AI PC Workloads"

    return "General AI"

@app.route("/compare", methods=["GET", "POST"])
def compare():

    devices = sorted(df["device"].unique())

    comparison = None
    winner = None
    device1 = request.args.get("device1")
    device2 = request.args.get("device2")

    if request.method == "POST" or (device1 and device2):

        if request.method == "POST":
            device1 = request.form["device1"]
            device2 = request.form["device2"]
            slug = (
                    device1.lower().replace(" ", "-")
                    + "-vs-" +
                    device2.lower().replace(" ", "-")
            )

            return redirect(f"/compare/{slug}")

        d1 = df[
            df["device"].str.lower() ==
            device1.lower()
            ]

        d2 = df[
            df["device"].str.lower() ==
            device2.lower()
            ]

        if not d1.empty and not d2.empty:

            tops1 = int(d1.iloc[0]["npu_tops"])
            tops2 = int(d2.iloc[0]["npu_tops"])

            if tops1 > tops2:
                winner = d1.iloc[0]["device"]
            elif tops2 > tops1:
                winner = d2.iloc[0]["device"]
            else:
                winner = "Tie"

            comparison = {
                "device1": {
                    "name": d1.iloc[0]["device"],
                    "platform": d1.iloc[0]["platform"],
                    "tops": tops1,
                    "chipset": d1.iloc[0]["chipset"],
                    "local_ai": get_local_ai(
                        d1.iloc[0]["platform"]
                    ),
                    "best_for": get_best_for(
                        d1.iloc[0]["platform"]
                    )
                },
                "device2": {
                    "name": d2.iloc[0]["device"],
                    "platform": d2.iloc[0]["platform"],
                    "tops": tops2,
                    "chipset": d2.iloc[0]["chipset"],
                    "local_ai": get_local_ai(
                        d2.iloc[0]["platform"]
                    ),
                    "best_for": get_best_for(
                        d2.iloc[0]["platform"]
                    )
                }
            }
    return render_template(
        "compare.html",
        devices=devices,
        comparison=comparison,
        winner=winner,
        selected_device1=device1,
        selected_device2=device2
    )


@app.route("/compare/<slug>")
def compare_slug(slug):

    parts = slug.split("-vs-")

    if len(parts) != 2:
        return "Invalid comparison"

    device1 = parts[0].replace("-", " ")
    device2 = parts[1].replace("-", " ")

    return redirect(
        f"/compare?device1={device1}&device2={device2}"
    )

@app.route("/top-ai-devices")
def top_ai_devices():

    master_df = pd.read_csv("devices_master.csv")

    devices = master_df.sort_values(
        by="npu_tops",
        ascending=False
    )

    return render_template(
        "top_ai_devices.html",
        devices=devices,
        page_title="Top AI Devices"
    )

@app.route("/top-ai-phones")
def top_ai_phones():

    master_df = pd.read_csv("devices_master.csv")

    phones = master_df[
        master_df["category"] == "Phones"
    ].sort_values(by="npu_tops", ascending=False)

    return render_template(
        "top_ai_devices.html",
        devices=phones,
        page_title="Top AI Phones"
    )

@app.route("/top-ai-tablets")
def top_ai_tablets():

    master_df = pd.read_csv("devices_master.csv")

    tablets = master_df[
        master_df["category"] == "Tablets"
    ].sort_values(by="npu_tops", ascending=False)

    return render_template(
        "top_ai_devices.html",
        devices=tablets,
        page_title="Top AI Tablets"
    )

@app.route("/top-ai-pcs")
def top_ai_pcs():

    master_df = pd.read_csv("devices_master.csv")

    pcs = master_df[
        master_df["category"] == "AI PCs"
    ].sort_values(by="npu_tops", ascending=False)

    return render_template(
        "top_ai_devices.html",
        devices=pcs,
        page_title="Top AI PCs"
    )

@app.route("/device/<device_name>")
def device_page(device_name):

    master_df = pd.read_csv("devices_master.csv")
    features_df = pd.read_csv("devices.csv")

    device_name = device_name.replace("-", " ")

    result = master_df[
        master_df["device"].str.lower()
        == device_name.lower()
    ]

    if result.empty:
        return "Device not found"

    device = result.iloc[0]

    feature_result = features_df[
        features_df["device"].str.lower()
        == device_name.lower()
        ]

    feature_data = None

    if not feature_result.empty:
        feature_data = feature_result.iloc[0].to_dict()

    category_devices = master_df[
        master_df["category"] == device["category"]
        ].sort_values(
        by="npu_tops",
        ascending=False
    ).reset_index(drop=True)

    rank_position = (category_devices[
                            category_devices["device"] == device["device"]
                            ].index[0]
    ) + 1

    total_devices = len(category_devices)

    related_devices = master_df[
        (master_df["category"] == device["category"]) &
        (master_df["device"].str.lower() != device["device"].lower())
        ].head(5)

    return render_template(
        "device.html",
        device=device,
        feature_data=feature_data,
        related_devices=related_devices,
        rank_position=rank_position,
        total_devices = total_devices
    )

@app.route("/platform/<platform_name>")
def platform_page(platform_name):

    master_df = pd.read_csv("devices_master.csv")

    if platform_name == "copilot-plus":
        platform_name = "Copilot+"
    else:
        platform_name = platform_name.replace("-", " ")

    devices = master_df[
        master_df["platform"].str.lower()
        == platform_name.lower()
    ]

    if devices.empty:
        return "Platform not found"

    descriptions = {
        "Galaxy Ai":
        "Galaxy AI is Samsung's AI platform combining on-device AI processing and cloud-powered AI features such as Live Translate, Note Assist, Circle to Search, and Generative Edit.",

        "Apple Intelligence":
        "Apple Intelligence is Apple's personal intelligence system designed for iPhone, iPad, and Mac. It combines on-device AI processing with Private Cloud Compute for privacy-focused AI experiences.",

        "Gemini Nano":
        "Gemini Nano is Google's on-device AI platform designed to run AI models locally on supported Android devices for faster and more private AI experiences.",

        "Copilot+":
        "Copilot+ is Microsoft's AI PC platform powered by dedicated NPUs, enabling local AI workloads such as Recall, Studio Effects, Live Captions, and AI-assisted productivity."
    }

    description = descriptions.get(
        platform_name.title(),
        "Explore AI devices and capabilities on this platform."
    )

    return render_template(
        "platform.html",
        platform_name=platform_name.title(),
        devices=devices.sort_values(
            by="npu_tops",
            ascending=False
        ),
        description=description
    )

@app.route("/methodology")
def methodology():
    return render_template("methodology.html")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(
        "static",
        "sitemap.xml"
    )

@app.route("/robots.txt")
def robots():
    return """
User-agent: *
Allow: /

Sitemap: https://ai.giznova.in/sitemap.xml
""", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(debug=True)