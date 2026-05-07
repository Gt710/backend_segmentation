```
<!-- MDSS Project Requirements -->
# Medical Decision Support System: Brain Tumor Segmentation

## Overview
A desktop-based diagnostic tool for radiologists to perform automated brain tumor segmentation on MRI scans using four modalities (T1, T1c, T2, FLAIR).

## Functional Requirements
- **File Upload:** 4 distinct zones for mandatory MRI modalities.
- **Analysis Action:** 'Predict' button to send files to `/predict`.
- **Visualization:** Central viewport for MRI slices with segmentation mask overlay (Edema, Necrosis, Active Tumor).
- **Results Panel:** Side/bottom card displaying:
    - Server status.
    - Anomaly metrics (volume of necrosis, edema, contrast enhancement).
    - Probabilistic classification (e.g., Glioma vs. Meningioma).

## Technical Architecture (Kotlin Jetpack Compose)
- **Pattern:** MVVM (ViewModel + StateFlow).
- **States:** Idle, Loading, Success, Error.
- **Network:** Stubbed multipart/form-data POST request.

## Visual Style
- **Theme:** Material Design 3.
- **Palette:** White, light grey, medical blue.
- **Tone:** Professional, precise, minimalist.

<!-- Segmentation Analysis Suite -->
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Brain Tumor Segmentation MDSS</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "tertiary": "#960010",
                        "outline": "#727783",
                        "on-surface": "#191c1e",
                        "on-tertiary-container": "#ffd0cb",
                        "on-tertiary": "#ffffff",
                        "primary-fixed": "#d6e3ff",
                        "on-tertiary-fixed-variant": "#930010",
                        "tertiary-container": "#bc1c21",
                        "on-primary-fixed": "#001b3d",
                        "surface-container": "#eceef1",
                        "surface": "#f7f9fc",
                        "on-secondary-fixed-variant": "#33495e",
                        "on-tertiary-fixed": "#410003",
                        "primary-container": "#005fb8",
                        "on-primary": "#ffffff",
                        "secondary-container": "#cbe2fc",
                        "error": "#ba1a1a",
                        "surface-variant": "#e0e3e6",
                        "on-secondary-fixed": "#041d30",
                        "secondary-fixed-dim": "#b2c9e2",
                        "on-secondary-container": "#4f657b",
                        "on-background": "#191c1e",
                        "tertiary-fixed-dim": "#ffb3ac",
                        "on-error-container": "#93000a",
                        "inverse-surface": "#2d3133",
                        "surface-container-lowest": "#ffffff",
                        "surface-dim": "#d8dadd",
                        "secondary-fixed": "#cee5ff",
                        "surface-container-highest": "#e0e3e6",
                        "on-secondary": "#ffffff",
                        "on-error": "#ffffff",
                        "inverse-primary": "#a8c8ff",
                        "on-primary-fixed-variant": "#00468b",
                        "error-container": "#ffdad6",
                        "surface-tint": "#005db5",
                        "background": "#f7f9fc",
                        "outline-variant": "#c2c6d4",
                        "surface-container-high": "#e6e8eb",
                        "surface-bright": "#f7f9fc",
                        "secondary": "#4a6077",
                        "surface-container-low": "#f2f4f7",
                        "primary-fixed-dim": "#a8c8ff",
                        "tertiary-fixed": "#ffdad6",
                        "primary": "#00488d",
                        "on-surface-variant": "#424752",
                        "on-primary-container": "#cadcff",
                        "inverse-on-surface": "#eff1f4"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                    },
                    "spacing": {
                        "md": "16px",
                        "xl": "32px",
                        "xs": "4px",
                        "gutter": "24px",
                        "base": "8px",
                        "margin-mobile": "16px",
                        "sm": "8px",
                        "lg": "24px",
                        "margin-desktop": "32px"
                    },
                    "fontFamily": {
                        "headline-md": ["Inter"],
                        "label-sm": ["Inter"],
                        "title-lg": ["Inter"],
                        "display-lg": ["Inter"],
                        "label-lg": ["Inter"],
                        "body-lg": ["Inter"],
                        "body-md": ["Inter"]
                    },
                    "fontSize": {
                        "headline-md": ["28px", { "lineHeight": "36px", "letterSpacing": "0px", "fontWeight": "600" }],
                        "label-sm": ["11px", { "lineHeight": "16px", "letterSpacing": "0.5px", "fontWeight": "500" }],
                        "title-lg": ["22px", { "lineHeight": "28px", "letterSpacing": "0px", "fontWeight": "500" }],
                        "display-lg": ["57px", { "lineHeight": "64px", "letterSpacing": "-0.25px", "fontWeight": "600" }],
                        "label-lg": ["14px", { "lineHeight": "20px", "letterSpacing": "0.1px", "fontWeight": "500" }],
                        "body-lg": ["16px", { "lineHeight": "24px", "letterSpacing": "0.5px", "fontWeight": "400" }],
                        "body-md": ["14px", { "lineHeight": "20px", "letterSpacing": "0.25px", "fontWeight": "400" }]
                    }
                }
            }
        }
    </script>
<style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-background text-on-background overflow-hidden h-screen w-full flex">
<!-- SideNavBar -->
<aside class="w-64 h-full border-r border-outline-variant bg-surface-container-low dark:bg-surface-container-low flex flex-col fixed left-0 top-0 overflow-y-auto z-20">
<div class="p-lg flex items-center gap-sm">
<img alt="Clinician profile" class="w-8 h-8 rounded-full border border-outline-variant" data-alt="A professional headshot of a clinician wearing medical scrubs, presented in a clean, brightly lit environment. The styling is sharp and clinical, utilizing a high-key light mode aesthetic." src="https://lh3.googleusercontent.com/aida-public/AB6AXuDUEW9MdpXcTfsQ9nm1Y13wPZ7gO2KGCm5VU-cdpYkhvX_MF_LgbeyDFKlbtQzWj8iG_Z47g2nCacacEHQ-G7OgUF1L57mt5YvH3AqowTPRbxLDjkH0eVoyZAFM52OTDGsyKNqGUF9wXIbbXC8DGOtc-4mm2VEbZfQWSDvBZs_bZUoezK_8Vz3oZB_b6f4APhz1q1qGdbfwalawNg_dCi9siSaTiddU1B5Ej29ljRGBQ-txvmw2ZZbh03Maqj36Cw4F-LC66H3bG7rH"/>
<div>
<h1 class="font-headline-md text-headline-md font-semibold text-primary dark:text-primary-fixed !text-lg !leading-tight">NeuroSegment AI</h1>
<p class="font-label-sm text-label-sm text-on-surface-variant">Radiology Suite v2.4</p>
</div>
</div>
<div class="px-md mb-lg">
<button class="w-full bg-primary-container text-on-primary font-label-lg text-label-lg py-sm px-md rounded-DEFAULT hover:bg-surface-tint transition-colors flex items-center justify-center gap-sm">
<span class="material-symbols-outlined text-[18px]">add</span>
                New Analysis
            </button>
</div>
<nav class="flex-1 px-md flex flex-col gap-xs">
<!-- Active Tab -->
<div class="flex items-center gap-md p-sm text-primary font-bold border-l-4 border-primary bg-secondary-container dark:bg-secondary-container rounded-r-DEFAULT cursor-pointer duration-150 ease-in-out">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">analytics</span>
<span class="font-body-md text-body-md">Segmentation</span>
</div>
<div class="flex items-center gap-md p-sm text-on-secondary-container dark:text-on-secondary-container-variant hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-colors cursor-pointer duration-150 ease-in-out rounded-DEFAULT ml-[4px]">
<span class="material-symbols-outlined">clinical_notes</span>
<span class="font-body-md text-body-md">Patient List</span>
</div>
<div class="flex items-center gap-md p-sm text-on-secondary-container dark:text-on-secondary-container-variant hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-colors cursor-pointer duration-150 ease-in-out rounded-DEFAULT ml-[4px]">
<span class="material-symbols-outlined">radiology</span>
<span class="font-body-md text-body-md">Image Acquisition</span>
</div>
<div class="flex items-center gap-md p-sm text-on-secondary-container dark:text-on-secondary-container-variant hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-colors cursor-pointer duration-150 ease-in-out rounded-DEFAULT ml-[4px]">
<span class="material-symbols-outlined">view_quilt</span>
<span class="font-body-md text-body-md">Metrics</span>
</div>
<div class="flex items-center gap-md p-sm text-on-secondary-container dark:text-on-secondary-container-variant hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-colors cursor-pointer duration-150 ease-in-out rounded-DEFAULT ml-[4px]">
<span class="material-symbols-outlined">description</span>
<span class="font-body-md text-body-md">Reports</span>
</div>
</nav>
<div class="p-md border-t border-outline-variant flex flex-col gap-xs">
<div class="flex items-center gap-md p-sm text-on-secondary-container dark:text-on-secondary-container-variant hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-colors cursor-pointer duration-150 ease-in-out rounded-DEFAULT ml-[4px]">
<span class="material-symbols-outlined">settings</span>
<span class="font-body-md text-body-md">Settings</span>
</div>
<div class="flex items-center gap-md p-sm text-on-secondary-container dark:text-on-secondary-container-variant hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-colors cursor-pointer duration-150 ease-in-out rounded-DEFAULT ml-[4px]">
<span class="material-symbols-outlined">help</span>
<span class="font-body-md text-body-md">Support</span>
</div>
</div>
</aside>
<!-- Main Content Area -->
<div class="flex-1 flex flex-col ml-64 min-h-screen">
<!-- TopAppBar -->
<header class="bg-surface dark:bg-surface border-b border-outline-variant docked full-width top-0 h-16 flex justify-between items-center w-full px-lg z-10 sticky">
<div class="flex items-center gap-lg">
<h2 class="font-headline-md text-headline-md font-bold text-primary dark:text-primary-fixed !text-xl">Brain Tumor Segmentation</h2>
<nav class="hidden md:flex gap-md h-full items-end pb-1">
<div class="font-title-lg text-title-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container-lowest dark:hover:bg-surface-container-low transition-all scale-98 active:opacity-80 transition-transform cursor-pointer !text-sm px-sm">Dashboard</div>
<div class="font-title-lg text-title-lg text-primary font-bold border-b-2 border-primary pb-1 hover:bg-surface-container-lowest dark:hover:bg-surface-container-low transition-all scale-98 active:opacity-80 transition-transform cursor-pointer !text-sm px-sm">Segmentation</div>
<div class="font-title-lg text-title-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container-lowest dark:hover:bg-surface-container-low transition-all scale-98 active:opacity-80 transition-transform cursor-pointer !text-sm px-sm">Archive</div>
<div class="font-title-lg text-title-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container-lowest dark:hover:bg-surface-container-low transition-all scale-98 active:opacity-80 transition-transform cursor-pointer !text-sm px-sm">Resources</div>
</nav>
</div>
<div class="flex items-center gap-md">
<button class="border border-outline-variant text-secondary font-label-lg text-label-lg py-xs px-md rounded-DEFAULT hover:bg-surface-container-low transition-colors">Export DICOM</button>
<button class="bg-primary-container text-on-primary font-label-lg text-label-lg py-xs px-md rounded-DEFAULT hover:bg-surface-tint transition-colors shadow-sm">Run AI Inference</button>
<div class="flex gap-sm border-l border-outline-variant pl-md ml-sm">
<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors">notifications</span>
<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors">account_circle</span>
</div>
</div>
</header>
<!-- Main Workspace -->
<main class="flex-1 p-margin-desktop bg-background overflow-y-auto">
<div class="grid grid-cols-12 gap-gutter h-full">
<!-- Left Column: Modality Uploads -->
<div class="col-span-3 flex flex-col gap-md h-full">
<h3 class="font-title-lg text-title-lg text-on-surface !text-base font-semibold mb-xs">MRI Modalities</h3>
<!-- Upload Zone T1 -->
<div class="border-2 border-dashed border-outline-variant bg-surface-container-low rounded-lg p-md flex flex-col items-center justify-center text-center hover:border-primary-container transition-colors cursor-pointer group h-full">
<span class="material-symbols-outlined text-primary-container text-3xl mb-sm group-hover:scale-110 transition-transform">upload_file</span>
<span class="font-label-lg text-label-lg text-on-surface font-semibold">T1-weighted</span>
<span class="font-body-md text-body-md text-on-surface-variant !text-xs mt-xs">Drag &amp; drop DICOM or NIfTI</span>
</div>
<!-- Upload Zone T1c -->
<div class="border border-outline-variant bg-surface-container-lowest rounded-lg p-md flex flex-col justify-between h-full relative overflow-hidden">
<div class="flex justify-between items-start">
<div>
<span class="font-label-lg text-label-lg text-on-surface font-semibold block">T1Gd (Contrast)</span>
<span class="font-body-md text-body-md text-on-surface-variant !text-xs">patient_142_t1c.nii.gz</span>
</div>
<span class="material-symbols-outlined text-primary-container text-xl">check_circle</span>
</div>
<div class="w-full bg-surface-container-high h-1 mt-md rounded-full overflow-hidden">
<div class="bg-primary-container h-full w-full"></div>
</div>
</div>
<!-- Upload Zone T2 -->
<div class="border-2 border-dashed border-outline-variant bg-surface-container-low rounded-lg p-md flex flex-col items-center justify-center text-center hover:border-primary-container transition-colors cursor-pointer group h-full">
<span class="material-symbols-outlined text-primary-container text-3xl mb-sm group-hover:scale-110 transition-transform">upload_file</span>
<span class="font-label-lg text-label-lg text-on-surface font-semibold">T2-weighted</span>
<span class="font-body-md text-body-md text-on-surface-variant !text-xs mt-xs">Drag &amp; drop DICOM or NIfTI</span>
</div>
<!-- Upload Zone FLAIR -->
<div class="border border-outline-variant bg-surface-container-lowest rounded-lg p-md flex flex-col justify-between h-full relative overflow-hidden">
<div class="flex justify-between items-start">
<div>
<span class="font-label-lg text-label-lg text-on-surface font-semibold block">FLAIR</span>
<span class="font-body-md text-body-md text-on-surface-variant !text-xs">patient_142_flair.nii.gz</span>
</div>
<span class="material-symbols-outlined text-primary-container text-xl">check_circle</span>
</div>
<div class="w-full bg-surface-container-high h-1 mt-md rounded-full overflow-hidden">
<div class="bg-primary-container h-full w-full"></div>
</div>
</div>
</div>
<!-- Center Column: Main Viewer -->
<div class="col-span-6 bg-surface-container-lowest border border-outline-variant rounded-xl flex flex-col h-full overflow-hidden relative">
<!-- Viewer Header -->
<div class="h-12 border-b border-outline-variant flex items-center justify-between px-md bg-surface">
<div class="flex items-center gap-sm">
<span class="font-label-lg text-label-lg font-semibold text-on-surface">Axial View</span>
<span class="text-outline-variant px-xs">|</span>
<span class="font-label-sm text-label-sm text-on-surface-variant">Slice 74 / 155</span>
</div>
<div class="flex items-center gap-md">
<span class="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[20px]">zoom_in</span>
<span class="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[20px]">contrast</span>
<span class="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[20px]">layers</span>
</div>
</div>
<!-- Viewer Canvas -->
<div class="flex-1 bg-black relative flex items-center justify-center overflow-hidden">
<!-- Placeholder for actual MRI Canvas. Using an image to simulate -->
<div class="relative w-full h-full max-w-[500px] max-h-[500px] m-auto flex items-center justify-center">
<img alt="Grayscale MRI Brain Scan" class="object-contain w-full h-full grayscale" data-alt="A highly detailed, grayscale medical MRI scan of a human brain in the axial plane. The image is strictly clinical, showing anatomical structures with high contrast. Superimposed over a specific region is a subtle, precise digital overlay using false colors: a thin green rim representing edema, a red core for necrosis, and yellow accents indicating active tumor regions. The overall aesthetic is serious, professional, and indicative of high-end medical diagnostic software in a light-mode interface context." src="https://lh3.googleusercontent.com/aida-public/AB6AXuBV-lwe4eXAPURrUiUebM95f2J0tcFf-hps9KIGVHfSC-ptTpznhjGTmRxpYncLZBLbE1RcF1sVLnbUB0cCrK_ra6bojKAGB2UIHRwDcV9g2elD_XcIMSXxtkzSfnfuYOcwATKN2JaYIqxREM7mCvjprd1FFs5AoO2qGhD3K75TQG2_6vNIf3Za-kaPpLuEGcZyaut4Ar0IRg3bY4IKwgSa7bVHvdXYfntiINr8OrcPFKmEfR278V9T9S7KvNIbV5lwoJIRCc_6hBBN"/>
<!-- Simulated Segmentation Overlay -->
<div class="absolute inset-0 flex items-center justify-center pointer-events-none">
<div class="w-48 h-32 rounded-full border-4 border-green-500/50 bg-yellow-500/30 flex items-center justify-center mix-blend-screen ml-12 mt-8 transform -rotate-12">
<div class="w-24 h-16 rounded-full bg-red-500/60 blur-[2px]"></div>
</div>
</div>
</div>
<!-- On-canvas tools -->
<div class="absolute right-md bottom-md bg-surface-container-lowest/90 backdrop-blur border border-outline-variant rounded-lg p-xs flex flex-col gap-xs">
<div class="p-xs hover:bg-surface-container-low rounded cursor-pointer text-on-surface flex items-center justify-center" title="Pan"><span class="material-symbols-outlined text-[18px]">pan_tool</span></div>
<div class="p-xs hover:bg-surface-container-low rounded cursor-pointer text-on-surface flex items-center justify-center" title="Measure"><span class="material-symbols-outlined text-[18px]">straighten</span></div>
</div>
</div>
<!-- Viewer Footer / Slider -->
<div class="h-16 border-t border-outline-variant flex items-center px-lg bg-surface">
<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary pr-md">skip_previous</span>
<div class="flex-1 mx-md relative flex items-center h-full">
<div class="w-full h-1 bg-surface-variant rounded-full">
<div class="h-full bg-primary-container rounded-full" style="width: 48%;"></div>
</div>
<div class="absolute w-4 h-4 bg-primary-container rounded-full shadow border-2 border-surface-container-lowest left-[48%] -ml-2 cursor-grab active:cursor-grabbing"></div>
</div>
<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary pl-md">skip_next</span>
</div>
</div>
<!-- Right Column: Results & Metrics -->
<div class="col-span-3 flex flex-col gap-md h-full">
<!-- Status Card -->
<div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-md">
<div class="flex items-center justify-between border-b border-outline-variant pb-sm mb-sm">
<span class="font-title-lg text-title-lg text-on-surface !text-base font-semibold">Analysis Status</span>
<span class="bg-secondary-container text-on-secondary-container font-label-sm text-label-sm px-2 py-1 rounded-full flex items-center gap-xs">
<span class="w-2 h-2 rounded-full bg-primary-container"></span> Complete
                            </span>
</div>
<p class="font-body-md text-body-md text-on-surface-variant !text-sm">Model: U-Net 3D (v4.1)<br/>Time: 00:02:14</p>
</div>
<!-- Classification Results -->
<div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-md">
<div class="border-b border-outline-variant pb-sm mb-sm">
<span class="font-title-lg text-title-lg text-on-surface !text-base font-semibold">Classification</span>
</div>
<div class="space-y-sm mt-md">
<div>
<div class="flex justify-between font-label-lg text-label-lg mb-xs">
<span class="text-on-surface">Glioma Probability</span>
<span class="font-bold text-primary">85%</span>
</div>
<div class="w-full bg-surface-container-high h-[4px] rounded-full overflow-hidden">
<div class="bg-primary-container h-full w-[85%]"></div>
</div>
</div>
<div>
<div class="flex justify-between font-label-lg text-label-lg mb-xs">
<span class="text-on-surface-variant">Meningioma Probability</span>
<span class="text-on-surface-variant">15%</span>
</div>
<div class="w-full bg-surface-container-high h-[4px] rounded-full overflow-hidden">
<div class="bg-outline-variant h-full w-[15%]"></div>
</div>
</div>
</div>
</div>
<!-- Volumetric Metrics -->
<div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-0 flex-1 flex flex-col">
<div class="p-md border-b border-outline-variant">
<span class="font-title-lg text-title-lg text-on-surface !text-base font-semibold">Volumetric Metrics</span>
</div>
<div class="flex-1 p-md flex flex-col justify-center gap-lg">
<!-- Metric 1 -->
<div class="flex items-center gap-md">
<div class="w-3 h-12 rounded-sm bg-red-500/80"></div>
<div>
<div class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Necrotic Core</div>
<div class="font-headline-md text-headline-md text-on-surface">14.2 <span class="text-sm font-normal text-on-surface-variant">cm³</span></div>
</div>
</div>
<!-- Metric 2 -->
<div class="flex items-center gap-md">
<div class="w-3 h-12 rounded-sm bg-green-500/80"></div>
<div>
<div class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Peritumoral Edema</div>
<div class="font-headline-md text-headline-md text-on-surface">42.8 <span class="text-sm font-normal text-on-surface-variant">cm³</span></div>
</div>
</div>
<!-- Metric 3 -->
<div class="flex items-center gap-md">
<div class="w-3 h-12 rounded-sm bg-yellow-500/80"></div>
<div>
<div class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Enhancing Tumor</div>
<div class="font-headline-md text-headline-md text-on-surface">8.5 <span class="text-sm font-normal text-on-surface-variant">cm³</span></div>
</div>
</div>
</div>
</div>
</div>
</div>
</main>
</div>
</body></html>

<!-- Design System -->
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Patient Archive - NeuroSegment AI</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "tertiary": "#960010",
                        "surface": "#f7f9fc",
                        "error-container": "#ffdad6",
                        "on-secondary-container": "#4f657b",
                        "surface-tint": "#005db5",
                        "on-error": "#ffffff",
                        "tertiary-fixed": "#ffdad6",
                        "on-background": "#191c1e",
                        "surface-container": "#eceef1",
                        "inverse-on-surface": "#eff1f4",
                        "tertiary-fixed-dim": "#ffb3ac",
                        "background": "#f7f9fc",
                        "on-tertiary-container": "#ffd0cb",
                        "primary-container": "#005fb8",
                        "on-surface": "#191c1e",
                        "on-primary-fixed-variant": "#00468b",
                        "on-tertiary": "#ffffff",
                        "outline-variant": "#c2c6d4",
                        "surface-variant": "#e0e3e6",
                        "on-tertiary-fixed-variant": "#930010",
                        "surface-bright": "#f7f9fc",
                        "on-secondary-fixed": "#041d30",
                        "on-surface-variant": "#424752",
                        "on-primary-fixed": "#001b3d",
                        "primary-fixed-dim": "#a8c8ff",
                        "on-secondary-fixed-variant": "#33495e",
                        "on-error-container": "#93000a",
                        "tertiary-container": "#bc1c21",
                        "inverse-surface": "#2d3133",
                        "on-primary": "#ffffff",
                        "secondary": "#4a6077",
                        "primary": "#00488d",
                        "on-tertiary-fixed": "#410003",
                        "secondary-container": "#cbe2fc",
                        "surface-container-low": "#f2f4f7",
                        "outline": "#727783",
                        "secondary-fixed-dim": "#b2c9e2",
                        "on-secondary": "#ffffff",
                        "inverse-primary": "#a8c8ff",
                        "secondary-fixed": "#cee5ff",
                        "on-primary-container": "#cadcff",
                        "surface-container-high": "#e6e8eb",
                        "surface-container-lowest": "#ffffff",
                        "surface-container-highest": "#e0e3e6",
                        "surface-dim": "#d8dadd",
                        "primary-fixed": "#d6e3ff",
                        "error": "#ba1a1a"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                    },
                    "spacing": {
                        "margin-desktop": "32px",
                        "xs": "4px",
                        "sm": "8px",
                        "md": "16px",
                        "lg": "24px",
                        "xl": "32px",
                        "margin-mobile": "16px",
                        "gutter": "24px",
                        "base": "8px"
                    },
                    "fontFamily": {
                        "headline-md": ["Inter"],
                        "label-sm": ["Inter"],
                        "display-lg": ["Inter"],
                        "title-lg": ["Inter"],
                        "body-md": ["Inter"],
                        "body-lg": ["Inter"],
                        "label-lg": ["Inter"]
                    },
                    "fontSize": {
                        "headline-md": ["28px", { "lineHeight": "36px", "letterSpacing": "0px", "fontWeight": "600" }],
                        "label-sm": ["11px", { "lineHeight": "16px", "letterSpacing": "0.5px", "fontWeight": "500" }],
                        "display-lg": ["57px", { "lineHeight": "64px", "letterSpacing": "-0.25px", "fontWeight": "600" }],
                        "title-lg": ["22px", { "lineHeight": "28px", "letterSpacing": "0px", "fontWeight": "500" }],
                        "body-md": ["14px", { "lineHeight": "20px", "letterSpacing": "0.25px", "fontWeight": "400" }],
                        "body-lg": ["16px", { "lineHeight": "24px", "letterSpacing": "0.5px", "fontWeight": "400" }],
                        "label-lg": ["14px", { "lineHeight": "20px", "letterSpacing": "0.1px", "fontWeight": "500" }]
                    }
                }
            }
        }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .material-symbols-outlined.filled {
            font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
    </style>
</head>
<body class="bg-background text-on-background font-body-md min-h-screen flex">
<!-- SideNavBar -->
<nav class="bg-surface dark:bg-surface border-r border-outline-variant dark:border-outline-variant docked h-full w-72 left-0 flex flex-col h-screen fixed left-0 top-0 py-lg px-md z-50">
<div class="mb-xl">
<h1 class="font-title-lg text-title-lg font-bold text-primary dark:text-primary-fixed">NeuroSegment AI</h1>
<p class="font-label-sm text-label-sm text-on-surface-variant mt-xs">Clinical Diagnostics</p>
</div>
<ul class="flex flex-col gap-sm flex-grow">
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">group</span>
                    Patient List
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">settings_remote</span>
                    Image Acquisition
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">layers</span>
                    Segmentation
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">analytics</span>
                    Metrics
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg bg-secondary-container dark:bg-secondary-container text-on-secondary-container font-semibold opacity-90 scale-[0.98] transition-all font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined filled">description</span>
                    Reports
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">settings</span>
                    Settings
                </a>
</li>
<li class="mt-auto">
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">help</span>
                    Support
                </a>
</li>
</ul>
</nav>
<div class="flex-1 ml-[288px] flex flex-col min-h-screen">
<!-- TopAppBar -->
<header class="bg-surface-container-lowest dark:bg-surface-container-lowest border-b border-outline-variant dark:border-outline-variant flex items-center justify-between h-16 w-full px-margin-desktop sticky top-0 z-40">
<div class="flex items-center gap-md">
<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors">menu</span>
<span class="font-title-lg text-title-lg font-bold text-primary dark:text-primary-fixed hidden">NeuroSegment AI</span> <!-- Hidden on desktop as per layout, brand is in sidebar -->
<nav class="hidden md:flex gap-lg">
<!-- Top nav omitted per rules since sidebar is present -->
</nav>
</div>
<div class="flex items-center gap-lg">
<div class="flex items-center gap-sm">
<button class="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors">notifications</button>
</div>
<div class="flex items-center gap-md">
<button class="border border-outline-variant text-secondary px-md py-sm rounded font-label-lg text-label-lg hover:bg-surface-container-low transition-colors">Export DICOM</button>
<button class="bg-primary-container text-on-primary px-md py-sm rounded font-label-lg text-label-lg hover:brightness-95 transition-all">Run AI Inference</button>
</div>
<div class="h-8 w-8 rounded-full bg-surface-variant flex items-center justify-center overflow-hidden border border-outline-variant cursor-pointer">
<img alt="User Clinician Avatar" class="h-full w-full object-cover" data-alt="A professional headshot of a medical clinician wearing a white coat, looking directly at the camera with a neutral, reassuring expression. The background is a clean, out-of-focus hospital corridor with bright, cool lighting consistent with a high-tech medical environment." src="https://lh3.googleusercontent.com/aida-public/AB6AXuBO3U_MfzWHmlCEZinN7_EV7wroDQHDitZ9DeXT5AkGZ11la0CiGhfTNG8ShO2r5RghZLPqu2FGWUIbyx9o5hekSdcRNlp2uowdunzHPWDoBJKBn5CWyPy4NoPkV0i50TueaVkGLuxAta3G7UYzUb8oM9YjUWnuXW1XrglzFFnRPfA-Y1GVA3NjuBmXqERoNGdXE46ifNYkIVxA3ObZ9TToAJ9J8deoxWlpsd9EHZOHZau3ODDVJVu133DC4ohc7zxDTVMCWj3cy1bG"/>
</div>
</div>
</header>
<!-- Main Content Canvas -->
<main class="flex-1 p-margin-desktop bg-surface">
<!-- Patient Summary Header -->
<section class="mb-xl">
<div class="flex items-start justify-between mb-md">
<div>
<div class="flex items-center gap-sm mb-xs">
<span class="material-symbols-outlined text-primary text-[20px]">person</span>
<h2 class="font-headline-md text-headline-md text-on-surface">DOE, Jane</h2>
</div>
<p class="font-body-md text-body-md text-on-surface-variant">ID: MRN-8472910 • DOB: 14-Aug-1965 (58y) • Female</p>
</div>
<div class="flex gap-sm">
<span class="bg-surface-container-high text-on-surface px-sm py-xs rounded font-label-sm text-label-sm uppercase tracking-wider">Diagnosis: Glioblastoma</span>
<span class="bg-surface-container-high text-on-surface px-sm py-xs rounded font-label-sm text-label-sm uppercase tracking-wider">Status: Post-Op Monitoring</span>
</div>
</div>
<!-- High Level Summary Stats -->
<div class="grid grid-cols-4 gap-gutter">
<div class="bg-surface-container-lowest border border-outline-variant rounded p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase mb-xs">Total Scans</span>
<span class="font-title-lg text-title-lg font-semibold text-on-surface">14</span>
</div>
<div class="bg-surface-container-lowest border border-outline-variant rounded p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase mb-xs">First Scan</span>
<span class="font-title-lg text-title-lg font-semibold text-on-surface">12-Jan-2022</span>
</div>
<div class="bg-surface-container-lowest border border-outline-variant rounded p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase mb-xs">Latest Scan</span>
<span class="font-title-lg text-title-lg font-semibold text-on-surface">04-Nov-2023</span>
</div>
<div class="bg-surface-container-lowest border border-outline-variant rounded p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase mb-xs">Volumetric Trend</span>
<div class="flex items-center gap-xs mt-xs">
<span class="material-symbols-outlined text-tertiary text-[20px]">trending_up</span>
<span class="font-title-lg text-title-lg font-semibold text-tertiary">+4.2%</span>
<span class="font-label-sm text-label-sm text-on-surface-variant ml-xs">(Last 3mo)</span>
</div>
</div>
</div>
</section>
<!-- Filters & Controls -->
<div class="flex items-center justify-between mb-lg pb-md border-b border-outline-variant">
<h3 class="font-title-lg text-title-lg text-on-surface">Segmentation Archive</h3>
<div class="flex items-center gap-md">
<div class="relative">
<span class="material-symbols-outlined absolute left-sm top-1/2 transform -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
<input class="pl-[32px] pr-md py-xs border border-outline-variant rounded bg-surface-container-lowest font-body-md text-body-md text-on-surface focus:border-primary focus:ring-1 focus:ring-primary w-64" placeholder="Search by date or metric..." type="text"/>
</div>
<button class="flex items-center gap-xs border border-outline-variant text-secondary px-sm py-xs rounded font-label-lg text-label-lg hover:bg-surface-container-low transition-colors">
<span class="material-symbols-outlined text-[18px]">filter_list</span>
                        Filter
                    </button>
<button class="flex items-center gap-xs border border-outline-variant text-secondary px-sm py-xs rounded font-label-lg text-label-lg hover:bg-surface-container-low transition-colors">
<span class="material-symbols-outlined text-[18px]">sort</span>
                        Sort: Newest
                    </button>
</div>
</div>
<!-- Gallery Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
<!-- Card 1 -->
<div class="bg-surface-container-lowest border border-outline-variant rounded flex flex-col overflow-hidden hover:border-primary transition-colors cursor-pointer group">
<div class="relative h-48 bg-black flex items-center justify-center border-b border-outline-variant">
<img alt="MRI Scan Thumbnail" class="h-full object-contain opacity-80 group-hover:opacity-100 transition-opacity" data-alt="A high-contrast black and white medical MRI scan of a human brain, showing axial slices. Artificial intelligence segmentation overlays highlight a specific tumor region in a subtle translucent blue tint. The image is stark, clinical, and precise, representing advanced diagnostic imaging technology." src="https://lh3.googleusercontent.com/aida-public/AB6AXuAdyWlt8wRVMEM5XUyGf6GE-UrCuaTai6Y3Vof6SCD48VBUiq2htFE27mH1w8EL6QSChTIwTTHG5XQzcYxsnNfou0WhsivOkE-DPq8FvyIAq4Uhj4taVHVT30qUgWExQHdxvyf6RNSX0Jtw7goXMz_f-ihbMVpkcSqC1hkxVCG1SHL8UIZUEdGj6V0BDL43FHNlD5WYeDlm150iREl2e-uNBA4wx_jWJqlir2TvHKKIy368ZhZ8omKk4Ff1d6hVFqBo1YlHUbzkFn4N"/>
<div class="absolute top-sm right-sm bg-surface-container-lowest/90 px-sm py-xs rounded font-label-sm text-label-sm text-on-surface backdrop-blur-sm">
                            T1 Post-Contrast
                        </div>
</div>
<div class="p-md flex-1 flex flex-col">
<div class="flex justify-between items-start mb-sm">
<div>
<h4 class="font-label-lg text-label-lg font-semibold text-on-surface">04-Nov-2023</h4>
<p class="font-body-md text-body-md text-on-surface-variant text-sm">Routine Follow-up</p>
</div>
<span class="material-symbols-outlined text-outline group-hover:text-primary transition-colors">arrow_forward</span>
</div>
<div class="mt-auto border-t border-surface-variant pt-sm grid grid-cols-2 gap-sm">
<div>
<p class="font-label-sm text-label-sm text-on-surface-variant uppercase">Tumor Volume</p>
<p class="font-body-lg text-body-lg text-on-surface font-medium">12.4 cm³</p>
</div>
<div>
<p class="font-label-sm text-label-sm text-on-surface-variant uppercase">Edema Volume</p>
<p class="font-body-lg text-body-lg text-on-surface font-medium">38.1 cm³</p>
</div>
</div>
</div>
</div>
<!-- Card 2 -->
<div class="bg-surface-container-lowest border border-outline-variant rounded flex flex-col overflow-hidden hover:border-primary transition-colors cursor-pointer group">
<div class="relative h-48 bg-black flex items-center justify-center border-b border-outline-variant">
<img alt="MRI Scan Thumbnail" class="h-full object-contain opacity-80 group-hover:opacity-100 transition-opacity" data-alt="A black and white axial MRI slice of a human brain, demonstrating detailed anatomical structures. A specific region of interest is outlined with a thin, precise primary blue contour line indicative of automated AI segmentation. The overall tone is sterile, highly technical, and focused on medical data." src="https://lh3.googleusercontent.com/aida-public/AB6AXuClTr09xfpz-ZQTNHkgneNuBAE0S7j1qL_xjyAkmhi7YuQBgSvXGU8Gywi7w91uSx-jYNoUuP1YPSRnf3WwzkjFZTV4bNuGNZZeOIZu_jXL3cXuKnKXEg4R33OrZon1u60B5hXKqpnsXJosCGbcUH-A83_IgJutqu5RmZ289TSnap_jyZk6207t38BBaQKvktAoFkmHAa9vaL-Cux_jdyOcsKeM8pZVZJEVyuOzUcVXHhZeklaaCk_w6PfZuNXRGdBGGt8kx06D5YfD"/>
<div class="absolute top-sm right-sm bg-surface-container-lowest/90 px-sm py-xs rounded font-label-sm text-label-sm text-on-surface backdrop-blur-sm">
                            T2 FLAIR
                        </div>
</div>
<div class="p-md flex-1 flex flex-col">
<div class="flex justify-between items-start mb-sm">
<div>
<h4 class="font-label-lg text-label-lg font-semibold text-on-surface">15-Aug-2023</h4>
<p class="font-body-md text-body-md text-on-surface-variant text-sm">Quarterly Assessment</p>
</div>
<span class="material-symbols-outlined text-outline group-hover:text-primary transition-colors">arrow_forward</span>
</div>
<div class="mt-auto border-t border-surface-variant pt-sm grid grid-cols-2 gap-sm">
<div>
<p class="font-label-sm text-label-sm text-on-surface-variant uppercase">Tumor Volume</p>
<p class="font-body-lg text-body-lg text-on-surface font-medium">11.9 cm³</p>
</div>
<div>
<p class="font-label-sm text-label-sm text-on-surface-variant uppercase">Edema Volume</p>
<p class="font-body-lg text-body-lg text-on-surface font-medium">36.5 cm³</p>
</div>
</div>
</div>
</div>
<!-- Card 3 -->
<div class="bg-surface-container-lowest border border-outline-variant rounded flex flex-col overflow-hidden hover:border-primary transition-colors cursor-pointer group">
<div class="relative h-48 bg-black flex items-center justify-center border-b border-outline-variant">
<img alt="MRI Scan Thumbnail" class="h-full object-contain opacity-80 group-hover:opacity-100 transition-opacity" data-alt="A stark black and white MRI brain scan image focusing on the cerebral cortex. Artificial intelligence markup is visible as a minimalist, glowing blue polygon enclosing an anomaly. The lighting is non-existent beyond the scan itself, emphasizing a pure diagnostic view suitable for clinical software interfaces." src="https://lh3.googleusercontent.com/aida-public/AB6AXuCyOLFaNsITZjOOpUDdAfG23P2VVKyymGjjaIvVqkvHf4RNAhUDs55oGpMjk5KIWXugGkP7lNPcBenjaeScvvf4gmS_MazCo5vARXdWO5C2AIc2OuG8FU2kwUYTTLhG24oV5y-XWu1fphy4cJPa_INqEDlAZF41NXe0Iam1wCv_aiNrNmGNRNmCwDEXnfKQ9aWGhjIyXrrd6hgm6r8Q1370LnmZE4vd3q_2cvLq-C0JKfTnaghw9R-My88kG4a0WBnnNkfScEZ2fyAD"/>
<div class="absolute top-sm right-sm bg-surface-container-lowest/90 px-sm py-xs rounded font-label-sm text-label-sm text-on-surface backdrop-blur-sm">
                            T1 Post-Contrast
                        </div>
</div>
<div class="p-md flex-1 flex flex-col">
<div class="flex justify-between items-start mb-sm">
<div>
<h4 class="font-label-lg text-label-lg font-semibold text-on-surface">22-May-2023</h4>
<p class="font-body-md text-body-md text-on-surface-variant text-sm">Post-Radiation Check</p>
</div>
<span class="material-symbols-outlined text-outline group-hover:text-primary transition-colors">arrow_forward</span>
</div>
<div class="mt-auto border-t border-surface-variant pt-sm grid grid-cols-2 gap-sm">
<div>
<p class="font-label-sm text-label-sm text-on-surface-variant uppercase">Tumor Volume</p>
<p class="font-body-lg text-body-lg text-on-surface font-medium">10.2 cm³</p>
</div>
<div>
<p class="font-label-sm text-label-sm text-on-surface-variant uppercase">Edema Volume</p>
<p class="font-body-lg text-body-lg text-on-surface font-medium">42.0 cm³</p>
</div>
</div>
</div>
</div>
</div>
<!-- Load More -->
<div class="mt-lg flex justify-center">
<button class="border border-outline-variant text-secondary px-lg py-sm rounded font-label-lg text-label-lg hover:bg-surface-container-low transition-colors flex items-center gap-sm">
                    Load Older Scans
                    <span class="material-symbols-outlined text-[18px]">expand_more</span>
</button>
</div>
</main>
</div>
</body></html>

<!-- Archive - NeuroSegment AI -->
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Patient List - NeuroSegment AI</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "tertiary": "#960010",
                        "surface": "#f7f9fc",
                        "error-container": "#ffdad6",
                        "on-secondary-container": "#4f657b",
                        "surface-tint": "#005db5",
                        "on-error": "#ffffff",
                        "tertiary-fixed": "#ffdad6",
                        "on-background": "#191c1e",
                        "surface-container": "#eceef1",
                        "inverse-on-surface": "#eff1f4",
                        "tertiary-fixed-dim": "#ffb3ac",
                        "background": "#f7f9fc",
                        "on-tertiary-container": "#ffd0cb",
                        "primary-container": "#005fb8",
                        "on-surface": "#191c1e",
                        "on-primary-fixed-variant": "#00468b",
                        "on-tertiary": "#ffffff",
                        "outline-variant": "#c2c6d4",
                        "surface-variant": "#e0e3e6",
                        "on-tertiary-fixed-variant": "#930010",
                        "surface-bright": "#f7f9fc",
                        "on-secondary-fixed": "#041d30",
                        "on-surface-variant": "#424752",
                        "on-primary-fixed": "#001b3d",
                        "primary-fixed-dim": "#a8c8ff",
                        "on-secondary-fixed-variant": "#33495e",
                        "on-error-container": "#93000a",
                        "tertiary-container": "#bc1c21",
                        "inverse-surface": "#2d3133",
                        "on-primary": "#ffffff",
                        "secondary": "#4a6077",
                        "primary": "#00488d",
                        "on-tertiary-fixed": "#410003",
                        "secondary-container": "#cbe2fc",
                        "surface-container-low": "#f2f4f7",
                        "outline": "#727783",
                        "secondary-fixed-dim": "#b2c9e2",
                        "on-secondary": "#ffffff",
                        "inverse-primary": "#a8c8ff",
                        "secondary-fixed": "#cee5ff",
                        "on-primary-container": "#cadcff",
                        "surface-container-high": "#e6e8eb",
                        "surface-container-lowest": "#ffffff",
                        "surface-container-highest": "#e0e3e6",
                        "surface-dim": "#d8dadd",
                        "primary-fixed": "#d6e3ff",
                        "error": "#ba1a1a"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                    },
                    "spacing": {
                        "margin-desktop": "32px",
                        "xs": "4px",
                        "sm": "8px",
                        "md": "16px",
                        "lg": "24px",
                        "xl": "32px",
                        "margin-mobile": "16px",
                        "gutter": "24px",
                        "base": "8px"
                    },
                    "fontFamily": {
                        "headline-md": ["Inter"],
                        "label-sm": ["Inter"],
                        "display-lg": ["Inter"],
                        "title-lg": ["Inter"],
                        "body-md": ["Inter"],
                        "body-lg": ["Inter"],
                        "label-lg": ["Inter"]
                    },
                    "fontSize": {
                        "headline-md": ["28px", { "lineHeight": "36px", "letterSpacing": "0px", "fontWeight": "600" }],
                        "label-sm": ["11px", { "lineHeight": "16px", "letterSpacing": "0.5px", "fontWeight": "500" }],
                        "display-lg": ["57px", { "lineHeight": "64px", "letterSpacing": "-0.25px", "fontWeight": "600" }],
                        "title-lg": ["22px", { "lineHeight": "28px", "letterSpacing": "0px", "fontWeight": "500" }],
                        "body-md": ["14px", { "lineHeight": "20px", "letterSpacing": "0.25px", "fontWeight": "400" }],
                        "body-lg": ["16px", { "lineHeight": "24px", "letterSpacing": "0.5px", "fontWeight": "400" }],
                        "label-lg": ["14px", { "lineHeight": "20px", "letterSpacing": "0.1px", "fontWeight": "500" }]
                    }
                }
            }
        }
    </script>
<style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-surface text-on-surface flex min-h-screen">
<!-- SideNavBar -->
<nav class="bg-surface border-r border-outline-variant docked h-full w-72 left-0 flex flex-col h-screen fixed left-0 top-0 py-lg px-md z-50">
<div class="flex items-center gap-md mb-xl px-sm">
<div class="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">neurology</span>
</div>
<div>
<h1 class="font-title-lg text-title-lg font-bold text-primary">NeuroSegment AI</h1>
<p class="font-label-sm text-label-sm text-on-surface-variant">Clinical Diagnostics</p>
</div>
</div>
<ul class="flex flex-col gap-sm flex-1">
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg bg-secondary-container text-on-secondary-container font-semibold font-label-lg text-label-lg hover:bg-surface-container transition-colors" href="#">
<span class="material-symbols-outlined">group</span>
                    Patient List
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors" href="#">
<span class="material-symbols-outlined">settings_remote</span>
                    Image Acquisition
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors" href="#">
<span class="material-symbols-outlined">layers</span>
                    Segmentation
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors" href="#">
<span class="material-symbols-outlined">analytics</span>
                    Metrics
                </a>
</li>
<li>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors" href="#">
<span class="material-symbols-outlined">description</span>
                    Reports
                </a>
</li>
</ul>
<div class="mt-auto border-t border-outline-variant pt-md flex flex-col gap-sm">
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors" href="#">
<span class="material-symbols-outlined">settings</span>
                Settings
            </a>
<a class="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors" href="#">
<span class="material-symbols-outlined">help</span>
                Support
            </a>
</div>
</nav>
<!-- Main Content Area -->
<div class="flex-1 ml-72 flex flex-col min-h-screen">
<!-- TopAppBar -->
<header class="bg-surface-container-lowest border-b border-outline-variant flex items-center justify-between h-16 w-full px-margin-desktop sticky top-0 z-40">
<div class="flex items-center gap-lg">
<h2 class="font-headline-md text-headline-md text-on-surface">Patient List</h2>
</div>
<div class="flex items-center gap-md">
<button class="w-10 h-10 rounded-full hover:bg-surface-container flex items-center justify-center text-on-surface-variant transition-colors">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="px-md py-sm rounded border border-outline-variant text-secondary font-label-lg text-label-lg hover:bg-surface-container transition-colors">
                    Export DICOM
                </button>
<button class="px-md py-sm rounded bg-primary-container text-on-primary-container font-label-lg text-label-lg hover:brightness-95 transition-all">
                    Run AI Inference
                </button>
<div class="w-8 h-8 rounded-full bg-surface-variant ml-sm overflow-hidden">
<img alt="User Clinician Avatar" class="w-full h-full object-cover" data-alt="A close-up, professional headshot of a medical professional wearing scrubs, set against a clean, light-mode sterile hospital background with soft, diffused lighting." src="https://lh3.googleusercontent.com/aida-public/AB6AXuDQ9SpIx2GHsT23bejRoD7Z4ap8J9OuuXQFjSl-wu3wsIrSi8vjrqKskmr0TiLwGwZW2010s7EN12v30wu81N0VOsFChsTNtclU7ou2lQEaDSlOSld9EDxQZhSip4ABIopZ8CU67OZjm2sE6Kin05Ry9nmiRtkFSO-umKQpF_-7HJfTjx9pbUXO-ovG60YUPKgQJ2GuqLgNIGXUpkHOzNySvhrR7zDZxPJ50q-uBMWFpuWMa46Xd3RlGRwGorfSM2uAOuTD87gLvgFC"/>
</div>
</div>
</header>
<!-- Main Canvas -->
<main class="flex-1 p-margin-desktop bg-surface flex flex-col gap-lg">
<!-- Filters & Search -->
<div class="flex items-center justify-between bg-surface-container-lowest p-md rounded-lg border border-outline-variant">
<div class="flex gap-sm">
<button class="px-md py-sm rounded-full bg-primary text-on-primary font-label-lg text-label-lg">All Patients</button>
<button class="px-md py-sm rounded-full border border-outline-variant text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors">Recent</button>
<button class="px-md py-sm rounded-full border border-outline-variant text-on-surface-variant font-label-lg text-label-lg hover:bg-surface-container transition-colors flex items-center gap-xs">
<span class="material-symbols-outlined text-[16px]">warning</span> Action Required
                    </button>
</div>
<div class="relative w-72">
<span class="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
<input class="w-full pl-xl pr-md py-sm bg-surface rounded border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary text-body-md font-body-md placeholder:text-on-surface-variant outline-none transition-all" placeholder="Search Patient ID, Name..." type="text"/>
</div>
</div>
<!-- Data Table Card -->
<div class="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden flex-1 flex flex-col">
<div class="overflow-x-auto">
<table class="w-full text-left border-collapse">
<thead>
<tr class="bg-surface-container-low border-b border-outline-variant">
<th class="py-sm px-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Patient ID</th>
<th class="py-sm px-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Name</th>
<th class="py-sm px-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Last Scan Date</th>
<th class="py-sm px-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Diagnosis</th>
<th class="py-sm px-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Analysis Status</th>
<th class="py-sm px-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider text-right">Actions</th>
</tr>
</thead>
<tbody class="font-body-md text-body-md text-on-surface divide-y divide-outline-variant">
<tr class="hover:bg-surface-container-low transition-colors group cursor-pointer">
<td class="py-md px-md font-medium">PT-2023-0891</td>
<td class="py-md px-md">Eleanor Vance</td>
<td class="py-md px-md text-on-surface-variant">Oct 24, 2023</td>
<td class="py-md px-md">
<span class="inline-flex items-center px-2 py-1 rounded bg-error-container text-on-error-container font-label-sm text-label-sm">
                                        Glioma - Grade IV
                                    </span>
</td>
<td class="py-md px-md">
<div class="flex items-center gap-sm">
<div class="w-2 h-2 rounded-full bg-primary-container"></div>
<span>Complete</span>
</div>
</td>
<td class="py-md px-md text-right">
<button class="p-sm rounded text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
<span class="material-symbols-outlined">arrow_forward_ios</span>
</button>
</td>
</tr>
<tr class="hover:bg-surface-container-low transition-colors group cursor-pointer">
<td class="py-md px-md font-medium">PT-2023-0892</td>
<td class="py-md px-md">Marcus Thorne</td>
<td class="py-md px-md text-on-surface-variant">Oct 23, 2023</td>
<td class="py-md px-md">
<span class="inline-flex items-center px-2 py-1 rounded bg-secondary-container text-on-secondary-container font-label-sm text-label-sm">
                                        Meningioma - Grade I
                                    </span>
</td>
<td class="py-md px-md">
<div class="flex items-center gap-sm">
<div class="w-2 h-2 rounded-full bg-surface-variant"></div>
<span>Pending Review</span>
</div>
</td>
<td class="py-md px-md text-right">
<button class="p-sm rounded text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
<span class="material-symbols-outlined">arrow_forward_ios</span>
</button>
</td>
</tr>
<tr class="hover:bg-surface-container-low transition-colors group cursor-pointer bg-surface-container-lowest">
<td class="py-md px-md font-medium">PT-2023-0893</td>
<td class="py-md px-md">Sarah Jenkins</td>
<td class="py-md px-md text-on-surface-variant">Oct 23, 2023</td>
<td class="py-md px-md">
<span class="text-on-surface-variant italic font-label-sm">Awaiting Scan</span>
</td>
<td class="py-md px-md">
<div class="flex items-center gap-sm">
<span class="material-symbols-outlined text-[16px] text-primary animate-spin">sync</span>
<span class="text-primary">Processing AI</span>
</div>
<div class="w-full bg-surface-container rounded-full h-1 mt-xs">
<div class="bg-primary h-1 rounded-full" style="width: 45%"></div>
</div>
</td>
<td class="py-md px-md text-right">
<button class="p-sm rounded text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
<span class="material-symbols-outlined">arrow_forward_ios</span>
</button>
</td>
</tr>
<tr class="hover:bg-surface-container-low transition-colors group cursor-pointer">
<td class="py-md px-md font-medium">PT-2023-0889</td>
<td class="py-md px-md">David Chen</td>
<td class="py-md px-md text-on-surface-variant">Oct 21, 2023</td>
<td class="py-md px-md">
<span class="inline-flex items-center px-2 py-1 rounded bg-secondary-container text-on-secondary-container font-label-sm text-label-sm">
                                        No Anomalies Detected
                                    </span>
</td>
<td class="py-md px-md">
<div class="flex items-center gap-sm">
<div class="w-2 h-2 rounded-full bg-primary-container"></div>
<span>Complete</span>
</div>
</td>
<td class="py-md px-md text-right">
<button class="p-sm rounded text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
<span class="material-symbols-outlined">arrow_forward_ios</span>
</button>
</td>
</tr>
</tbody>
</table>
</div>
<!-- Pagination Footer -->
<div class="border-t border-outline-variant p-sm flex items-center justify-between bg-surface-container-low mt-auto">
<span class="font-body-md text-body-md text-on-surface-variant ml-md">Showing 1-4 of 128 Patients</span>
<div class="flex gap-xs mr-md">
<button class="p-xs rounded hover:bg-surface-container text-on-surface-variant disabled:opacity-50">
<span class="material-symbols-outlined">chevron_left</span>
</button>
<button class="p-xs rounded hover:bg-surface-container text-on-surface-variant">
<span class="material-symbols-outlined">chevron_right</span>
</button>
</div>
</div>
</div>
</main>
</div>
</body></html>

<!-- Patient List - NeuroSegment AI -->
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Export Results - NeuroSegment AI</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "tertiary": "#960010",
                        "surface": "#f7f9fc",
                        "error-container": "#ffdad6",
                        "on-secondary-container": "#4f657b",
                        "surface-tint": "#005db5",
                        "on-error": "#ffffff",
                        "tertiary-fixed": "#ffdad6",
                        "on-background": "#191c1e",
                        "surface-container": "#eceef1",
                        "inverse-on-surface": "#eff1f4",
                        "tertiary-fixed-dim": "#ffb3ac",
                        "background": "#f7f9fc",
                        "on-tertiary-container": "#ffd0cb",
                        "primary-container": "#005fb8",
                        "on-surface": "#191c1e",
                        "on-primary-fixed-variant": "#00468b",
                        "on-tertiary": "#ffffff",
                        "outline-variant": "#c2c6d4",
                        "surface-variant": "#e0e3e6",
                        "on-tertiary-fixed-variant": "#930010",
                        "surface-bright": "#f7f9fc",
                        "on-secondary-fixed": "#041d30",
                        "on-surface-variant": "#424752",
                        "on-primary-fixed": "#001b3d",
                        "primary-fixed-dim": "#a8c8ff",
                        "on-secondary-fixed-variant": "#33495e",
                        "on-error-container": "#93000a",
                        "tertiary-container": "#bc1c21",
                        "inverse-surface": "#2d3133",
                        "on-primary": "#ffffff",
                        "secondary": "#4a6077",
                        "primary": "#00488d",
                        "on-tertiary-fixed": "#410003",
                        "secondary-container": "#cbe2fc",
                        "surface-container-low": "#f2f4f7",
                        "outline": "#727783",
                        "secondary-fixed-dim": "#b2c9e2",
                        "on-secondary": "#ffffff",
                        "inverse-primary": "#a8c8ff",
                        "secondary-fixed": "#cee5ff",
                        "on-primary-container": "#cadcff",
                        "surface-container-high": "#e6e8eb",
                        "surface-container-lowest": "#ffffff",
                        "surface-container-highest": "#e0e3e6",
                        "surface-dim": "#d8dadd",
                        "primary-fixed": "#d6e3ff",
                        "error": "#ba1a1a"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                    },
                    "spacing": {
                        "margin-desktop": "32px",
                        "xs": "4px",
                        "sm": "8px",
                        "md": "16px",
                        "lg": "24px",
                        "xl": "32px",
                        "margin-mobile": "16px",
                        "gutter": "24px",
                        "base": "8px"
                    },
                    "fontFamily": {
                        "headline-md": ["Inter"],
                        "label-sm": ["Inter"],
                        "display-lg": ["Inter"],
                        "title-lg": ["Inter"],
                        "body-md": ["Inter"],
                        "body-lg": ["Inter"],
                        "label-lg": ["Inter"]
                    },
                    "fontSize": {
                        "headline-md": ["28px", { "lineHeight": "36px", "letterSpacing": "0px", "fontWeight": "600" }],
                        "label-sm": ["11px", { "lineHeight": "16px", "letterSpacing": "0.5px", "fontWeight": "500" }],
                        "display-lg": ["57px", { "lineHeight": "64px", "letterSpacing": "-0.25px", "fontWeight": "600" }],
                        "title-lg": ["22px", { "lineHeight": "28px", "letterSpacing": "0px", "fontWeight": "500" }],
                        "body-md": ["14px", { "lineHeight": "20px", "letterSpacing": "0.25px", "fontWeight": "400" }],
                        "body-lg": ["16px", { "lineHeight": "24px", "letterSpacing": "0.5px", "fontWeight": "400" }],
                        "label-lg": ["14px", { "lineHeight": "20px", "letterSpacing": "0.1px", "fontWeight": "500" }]
                    }
                }
            }
        }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .material-symbols-outlined.filled {
            font-variation-settings: 'FILL' 1;
        }
        /* Custom Checkbox Style for Clinical Precision */
        input[type="checkbox"]:checked {
            background-color: #005fb8;
            border-color: #005fb8;
        }
        input[type="radio"]:checked {
            border-color: #005fb8;
        }
        input[type="radio"]:checked:after {
            background-color: #005fb8;
        }
    </style>
</head>
<body class="bg-surface-container-high h-screen w-screen flex items-center justify-center font-body-md text-on-surface antialiased overflow-hidden">
<!-- Scrim / Backdrop -->
<div class="fixed inset-0 bg-on-background/40 backdrop-blur-sm z-40 transition-opacity flex items-center justify-center p-md sm:p-lg">
<!-- Modal Container -->
<div class="bg-surface-container-lowest rounded-xl w-full max-w-2xl shadow-xl border border-outline-variant flex flex-col z-50 overflow-hidden transform transition-all">
<!-- Modal Header -->
<div class="px-lg py-md border-b border-outline-variant flex items-center justify-between bg-surface-container-lowest">
<div class="flex items-center gap-sm text-primary">
<span class="material-symbols-outlined text-title-lg">ios_share</span>
<h2 class="font-title-lg text-title-lg text-on-surface">Export Segmentation Results</h2>
</div>
<button class="text-on-surface-variant hover:text-on-surface transition-colors p-xs rounded-full hover:bg-surface-container">
<span class="material-symbols-outlined">close</span>
</button>
</div>
<!-- Modal Body -->
<div class="p-lg flex-1 overflow-y-auto">
<div class="space-y-xl">
<!-- Format Selection Section -->
<section>
<h3 class="font-label-lg text-label-lg text-on-surface mb-sm">Export Format</h3>
<p class="font-body-md text-body-md text-on-surface-variant mb-md">Select the primary format for the segmentation output.</p>
<div class="grid grid-cols-1 md:grid-cols-3 gap-md">
<!-- Format Option 1: DICOM -->
<label class="relative flex flex-col p-md border rounded-lg cursor-pointer transition-all border-primary-container bg-surface-container-lowest hover:bg-surface-container shadow-sm">
<input checked="" class="sr-only" name="export_format" type="radio" value="dicom"/>
<div class="flex items-center justify-between mb-sm">
<span class="material-symbols-outlined text-primary-container filled">folder_zip</span>
<div class="w-4 h-4 rounded-full border-2 border-primary-container flex items-center justify-center">
<div class="w-2 h-2 rounded-full bg-primary-container"></div>
</div>
</div>
<span class="font-label-lg text-label-lg text-on-surface block">DICOM-RT</span>
<span class="font-label-sm text-label-sm text-on-surface-variant block mt-xs">Includes full metadata</span>
</label>
<!-- Format Option 2: NIfTI -->
<label class="relative flex flex-col p-md border border-outline-variant rounded-lg cursor-pointer transition-all bg-surface-container-lowest hover:bg-surface-container hover:border-outline">
<input class="sr-only" name="export_format" type="radio" value="nifti"/>
<div class="flex items-center justify-between mb-sm">
<span class="material-symbols-outlined text-on-surface-variant">layers</span>
<div class="w-4 h-4 rounded-full border-2 border-outline-variant"></div>
</div>
<span class="font-label-lg text-label-lg text-on-surface block">NIfTI Masks</span>
<span class="font-label-sm text-label-sm text-on-surface-variant block mt-xs">Binary .nii.gz format</span>
</label>
<!-- Format Option 3: PDF -->
<label class="relative flex flex-col p-md border border-outline-variant rounded-lg cursor-pointer transition-all bg-surface-container-lowest hover:bg-surface-container hover:border-outline">
<input class="sr-only" name="export_format" type="radio" value="pdf"/>
<div class="flex items-center justify-between mb-sm">
<span class="material-symbols-outlined text-on-surface-variant">description</span>
<div class="w-4 h-4 rounded-full border-2 border-outline-variant"></div>
</div>
<span class="font-label-lg text-label-lg text-on-surface block">PDF Report</span>
<span class="font-label-sm text-label-sm text-on-surface-variant block mt-xs">Summary with metrics</span>
</label>
</div>
</section>
<!-- Divider -->
<div class="h-px w-full bg-outline-variant"></div>
<!-- Modalities Selection Section -->
<section>
<h3 class="font-label-lg text-label-lg text-on-surface mb-sm">Include Modalities</h3>
<p class="font-body-md text-body-md text-on-surface-variant mb-md">Select the specific volumes to include in this export package.</p>
<div class="bg-surface border border-outline-variant rounded-lg overflow-hidden">
<label class="flex items-center px-md py-sm border-b border-outline-variant hover:bg-surface-container transition-colors cursor-pointer">
<input checked="" class="w-4 h-4 text-primary-container bg-surface-container-lowest border-outline rounded focus:ring-primary-container focus:ring-2" type="checkbox"/>
<span class="ml-md font-body-md text-body-md text-on-surface">T1-weighted (Pre-contrast)</span>
</label>
<label class="flex items-center px-md py-sm border-b border-outline-variant hover:bg-surface-container transition-colors cursor-pointer">
<input checked="" class="w-4 h-4 text-primary-container bg-surface-container-lowest border-outline rounded focus:ring-primary-container focus:ring-2" type="checkbox"/>
<span class="ml-md font-body-md text-body-md text-on-surface">T1-weighted (Post-contrast)</span>
</label>
<label class="flex items-center px-md py-sm border-b border-outline-variant hover:bg-surface-container transition-colors cursor-pointer">
<input class="w-4 h-4 text-primary-container bg-surface-container-lowest border-outline rounded focus:ring-primary-container focus:ring-2" type="checkbox"/>
<span class="ml-md font-body-md text-body-md text-on-surface">T2-weighted (FLAIR)</span>
</label>
<label class="flex items-center px-md py-sm hover:bg-surface-container transition-colors cursor-pointer">
<input class="w-4 h-4 text-primary-container bg-surface-container-lowest border-outline rounded focus:ring-primary-container focus:ring-2" type="checkbox"/>
<span class="ml-md font-body-md text-body-md text-on-surface">Apparent Diffusion Coefficient (ADC)</span>
</label>
</div>
</section>
<!-- Advanced Options (Collapsed state implied) -->
<section class="flex items-center justify-between p-md bg-surface border border-outline-variant rounded-lg">
<div class="flex items-center gap-sm">
<span class="material-symbols-outlined text-on-surface-variant">tune</span>
<span class="font-label-lg text-label-lg text-on-surface">Anonymize Patient Data (HIPAA Compliant)</span>
</div>
<label class="relative inline-flex items-center cursor-pointer">
<input checked="" class="sr-only peer" type="checkbox" value=""/>
<div class="w-9 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary-container"></div>
</label>
</section>
</div>
</div>
<!-- Modal Footer (Actions) -->
<div class="px-lg py-md border-t border-outline-variant bg-surface-container-lowest flex justify-end gap-md">
<button class="px-lg py-sm font-label-lg text-label-lg text-secondary border border-outline-variant rounded hover:bg-surface-container transition-colors focus:outline-none focus:ring-2 focus:ring-secondary/50">
                    Cancel
                </button>
<button class="px-lg py-sm font-label-lg text-label-lg text-on-primary bg-primary-container rounded hover:bg-primary transition-colors shadow-sm flex items-center gap-xs focus:outline-none focus:ring-2 focus:ring-primary-container/50">
<span class="material-symbols-outlined text-[18px]">download</span>
                    Export Results
                </button>
</div>
</div>
</div>
</body></html>

<!-- Export Results - NeuroSegment AI -->
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>NeuroSegment AI - Metrics</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "tertiary": "#960010",
                        "surface": "#f7f9fc",
                        "error-container": "#ffdad6",
                        "on-secondary-container": "#4f657b",
                        "surface-tint": "#005db5",
                        "on-error": "#ffffff",
                        "tertiary-fixed": "#ffdad6",
                        "on-background": "#191c1e",
                        "surface-container": "#eceef1",
                        "inverse-on-surface": "#eff1f4",
                        "tertiary-fixed-dim": "#ffb3ac",
                        "background": "#f7f9fc",
                        "on-tertiary-container": "#ffd0cb",
                        "primary-container": "#005fb8",
                        "on-surface": "#191c1e",
                        "on-primary-fixed-variant": "#00468b",
                        "on-tertiary": "#ffffff",
                        "outline-variant": "#c2c6d4",
                        "surface-variant": "#e0e3e6",
                        "on-tertiary-fixed-variant": "#930010",
                        "surface-bright": "#f7f9fc",
                        "on-secondary-fixed": "#041d30",
                        "on-surface-variant": "#424752",
                        "on-primary-fixed": "#001b3d",
                        "primary-fixed-dim": "#a8c8ff",
                        "on-secondary-fixed-variant": "#33495e",
                        "on-error-container": "#93000a",
                        "tertiary-container": "#bc1c21",
                        "inverse-surface": "#2d3133",
                        "on-primary": "#ffffff",
                        "secondary": "#4a6077",
                        "primary": "#00488d",
                        "on-tertiary-fixed": "#410003",
                        "secondary-container": "#cbe2fc",
                        "surface-container-low": "#f2f4f7",
                        "outline": "#727783",
                        "secondary-fixed-dim": "#b2c9e2",
                        "on-secondary": "#ffffff",
                        "inverse-primary": "#a8c8ff",
                        "secondary-fixed": "#cee5ff",
                        "on-primary-container": "#cadcff",
                        "surface-container-high": "#e6e8eb",
                        "surface-container-lowest": "#ffffff",
                        "surface-container-highest": "#e0e3e6",
                        "surface-dim": "#d8dadd",
                        "primary-fixed": "#d6e3ff",
                        "error": "#ba1a1a"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                    },
                    "spacing": {
                        "margin-desktop": "32px",
                        "xs": "4px",
                        "sm": "8px",
                        "md": "16px",
                        "lg": "24px",
                        "xl": "32px",
                        "margin-mobile": "16px",
                        "gutter": "24px",
                        "base": "8px"
                    },
                    "fontFamily": {
                        "headline-md": ["Inter"],
                        "label-sm": ["Inter"],
                        "display-lg": ["Inter"],
                        "title-lg": ["Inter"],
                        "body-md": ["Inter"],
                        "body-lg": ["Inter"],
                        "label-lg": ["Inter"]
                    },
                    "fontSize": {
                        "headline-md": ["28px", { "lineHeight": "36px", "letterSpacing": "0px", "fontWeight": "600" }],
                        "label-sm": ["11px", { "lineHeight": "16px", "letterSpacing": "0.5px", "fontWeight": "500" }],
                        "display-lg": ["57px", { "lineHeight": "64px", "letterSpacing": "-0.25px", "fontWeight": "600" }],
                        "title-lg": ["22px", { "lineHeight": "28px", "letterSpacing": "0px", "fontWeight": "500" }],
                        "body-md": ["14px", { "lineHeight": "20px", "letterSpacing": "0.25px", "fontWeight": "400" }],
                        "body-lg": ["16px", { "lineHeight": "24px", "letterSpacing": "0.5px", "fontWeight": "400" }],
                        "label-lg": ["14px", { "lineHeight": "20px", "letterSpacing": "0.1px", "fontWeight": "500" }]
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-surface text-on-surface font-body-md min-h-screen flex">
<!-- SideNavBar -->
<nav class="bg-surface dark:bg-surface border-r border-outline-variant dark:border-outline-variant docked h-full w-72 left-0 flex flex-col h-screen fixed left-0 top-0 py-lg px-md z-50">
<div class="flex items-center gap-sm mb-xl">
<div class="w-10 h-10 bg-primary-container rounded-DEFAULT flex items-center justify-center">
<span class="material-symbols-outlined text-on-primary-container">biotech</span>
</div>
<div>
<h1 class="font-title-lg text-title-lg font-bold text-primary dark:text-primary-fixed">NeuroSegment AI</h1>
<p class="font-label-sm text-label-sm text-on-surface-variant">Clinical Diagnostics</p>
</div>
</div>
<div class="flex flex-col gap-xs">
<a class="flex items-center gap-md px-md py-sm rounded-DEFAULT text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">group</span>
                Patient List
            </a>
<a class="flex items-center gap-md px-md py-sm rounded-DEFAULT text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">settings_remote</span>
                Image Acquisition
            </a>
<a class="flex items-center gap-md px-md py-sm rounded-DEFAULT text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">layers</span>
                Segmentation
            </a>
<a class="flex items-center gap-md px-md py-sm rounded-DEFAULT bg-secondary-container dark:bg-secondary-container text-on-secondary-container font-semibold font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">analytics</span>
                Metrics
            </a>
<a class="flex items-center gap-md px-md py-sm rounded-DEFAULT text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">description</span>
                Reports
            </a>
<a class="flex items-center gap-md px-md py-sm rounded-DEFAULT text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg mt-auto" href="#">
<span class="material-symbols-outlined">settings</span>
                Settings
            </a>
<a class="flex items-center gap-md px-md py-sm rounded-DEFAULT text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high transition-colors font-label-lg text-label-lg" href="#">
<span class="material-symbols-outlined">help</span>
                Support
            </a>
</div>
</nav>
<!-- Main Content Wrapper -->
<div class="flex-1 ml-72 flex flex-col min-h-screen">
<!-- TopAppBar -->
<header class="bg-surface-container-lowest dark:bg-surface-container-lowest border-b border-outline-variant dark:border-outline-variant docked full-width top-0 flex items-center justify-between h-16 w-full pl-lg pr-margin-desktop bg-surface dark:bg-surface z-40 sticky">
<div class="flex items-center gap-md">
<h2 class="font-headline-md text-headline-md text-primary dark:text-primary-fixed">Patient PT-4092 Metrics</h2>
</div>
<div class="flex items-center gap-md">
<button class="w-10 h-10 rounded-full hover:bg-surface-container transition-colors flex items-center justify-center text-on-surface-variant">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="px-md py-sm rounded-DEFAULT border border-outline-variant text-secondary font-label-lg text-label-lg hover:bg-surface-container transition-colors">
                    Export DICOM
                </button>
<button class="px-md py-sm rounded-DEFAULT bg-primary-container text-on-primary font-label-lg text-label-lg hover:brightness-95 transition-all">
                    Run AI Inference
                </button>
<div class="w-10 h-10 rounded-full bg-surface-variant overflow-hidden border border-outline-variant ml-sm">
<img alt="User Clinician Avatar" class="w-full h-full object-cover" data-alt="A close-up portrait of a medical professional, likely a clinician or doctor, wearing standard medical scrubs. The lighting is clean, bright, and clinical, emphasizing professionalism and expertise. The background is a soft, out-of-focus hospital or clinic setting with neutral tones." src="https://lh3.googleusercontent.com/aida-public/AB6AXuC7hRk_fRvXLEsvbMFrNgZYZrzvPmpnn9VgrVuSPOscUBM1NW2y2Hk972W5dQACGTjXuByYuWwi1KKcBteRP7r2qyBCSO9mFT0NVwFrFnJyl5w9gZfXYvQBvbWpeZk2DklpIvu4pW6VCU8Nj2U4wUcjGVIWVyC-IC7pDd3IB5ziDUBh0Gu9MRVHqJSOgfqpr__f3baAg6SxM7b_LZYZhyzF8bG9kUTdNop5nNjxqnlccAjSmJO1U9T73BEBGqGjWJLk-EDnDL1hRwgr"/>
</div>
</div>
</header>
<!-- Dashboard Content -->
<main class="flex-1 p-margin-desktop bg-surface">
<div class="grid grid-cols-12 gap-gutter">
<!-- Summary Metrics Row -->
<div class="col-span-12 grid grid-cols-4 gap-gutter mb-lg">
<div class="bg-surface-container-lowest border border-outline-variant rounded-DEFAULT p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-xs">Total Tumor Volume</span>
<div class="flex items-baseline gap-sm">
<span class="font-headline-md text-headline-md text-on-surface">42.5</span>
<span class="font-body-md text-body-md text-on-surface-variant">cm³</span>
</div>
<div class="mt-sm flex items-center gap-xs text-error">
<span class="material-symbols-outlined text-[16px]">trending_up</span>
<span class="font-label-sm text-label-sm">+4.2% vs Baseline</span>
</div>
</div>
<div class="bg-surface-container-lowest border border-outline-variant rounded-DEFAULT p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-xs">Edema Volume</span>
<div class="flex items-baseline gap-sm">
<span class="font-headline-md text-headline-md text-on-surface">18.2</span>
<span class="font-body-md text-body-md text-on-surface-variant">cm³</span>
</div>
<div class="mt-sm flex items-center gap-xs text-primary">
<span class="material-symbols-outlined text-[16px]">trending_down</span>
<span class="font-label-sm text-label-sm">-1.5% vs Baseline</span>
</div>
</div>
<div class="bg-surface-container-lowest border border-outline-variant rounded-DEFAULT p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-xs">Necrosis Volume</span>
<div class="flex items-baseline gap-sm">
<span class="font-headline-md text-headline-md text-on-surface">8.4</span>
<span class="font-body-md text-body-md text-on-surface-variant">cm³</span>
</div>
<div class="mt-sm flex items-center gap-xs text-error">
<span class="material-symbols-outlined text-[16px]">trending_up</span>
<span class="font-label-sm text-label-sm">+8.1% vs Baseline</span>
</div>
</div>
<div class="bg-surface-container-lowest border border-outline-variant rounded-DEFAULT p-md flex flex-col">
<span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-xs">Active Tumor</span>
<div class="flex items-baseline gap-sm">
<span class="font-headline-md text-headline-md text-on-surface">15.9</span>
<span class="font-body-md text-body-md text-on-surface-variant">cm³</span>
</div>
<div class="mt-sm flex items-center gap-xs text-on-surface-variant">
<span class="material-symbols-outlined text-[16px]">trending_flat</span>
<span class="font-label-sm text-label-sm">0.0% vs Baseline</span>
</div>
</div>
</div>
<!-- Main Longitudinal Chart -->
<div class="col-span-8 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT flex flex-col">
<div class="p-md border-b border-outline-variant flex justify-between items-center">
<h3 class="font-title-lg text-title-lg text-on-surface">Longitudinal Volume Analysis</h3>
<div class="flex gap-sm">
<button class="px-sm py-xs border border-outline-variant rounded-DEFAULT font-label-sm text-label-sm text-on-surface-variant bg-surface-container">3M</button>
<button class="px-sm py-xs border border-outline-variant rounded-DEFAULT font-label-sm text-label-sm text-on-surface-variant hover:bg-surface-container">6M</button>
<button class="px-sm py-xs border border-outline-variant rounded-DEFAULT font-label-sm text-label-sm text-on-surface-variant hover:bg-surface-container">1Y</button>
</div>
</div>
<div class="p-md flex-1 relative min-h-[300px]">
<!-- Placeholder for Line Chart -->
<div class="absolute inset-md flex items-end gap-md">
<!-- Y Axis -->
<div class="flex flex-col justify-between h-full text-label-sm text-on-surface-variant pr-sm border-r border-outline-variant">
<span>50</span>
<span>40</span>
<span>30</span>
<span>20</span>
<span>10</span>
<span>0</span>
</div>
<!-- Chart Area (Simulated) -->
<div class="flex-1 h-full relative">
<!-- Grid Lines -->
<div class="absolute inset-0 flex flex-col justify-between">
<div class="w-full h-px bg-surface-variant"></div>
<div class="w-full h-px bg-surface-variant"></div>
<div class="w-full h-px bg-surface-variant"></div>
<div class="w-full h-px bg-surface-variant"></div>
<div class="w-full h-px bg-surface-variant"></div>
<div class="w-full h-px bg-outline-variant"></div>
</div>
<!-- Simulated Lines (SVG would be ideal here, using simple divs for illustration) -->
<svg class="absolute inset-0 w-full h-full" preserveaspectratio="none">
<path d="M 0,200 L 100,180 L 200,190 L 300,150 L 400,160 L 500,120 L 600,100" fill="none" stroke="#005fb8" stroke-width="2"></path>
<path d="M 0,250 L 100,240 L 200,245 L 300,230 L 400,220 L 500,210 L 600,200" fill="none" stroke="#4a6077" stroke-dasharray="4" stroke-width="2"></path>
<path d="M 0,280 L 100,270 L 200,275 L 300,260 L 400,250 L 500,240 L 600,230" fill="none" stroke="#960010" stroke-width="2"></path>
</svg>
</div>
</div>
</div>
<div class="p-sm flex justify-center gap-lg border-t border-outline-variant">
<div class="flex items-center gap-xs font-label-sm text-label-sm text-on-surface-variant">
<div class="w-3 h-3 rounded-sm bg-primary-container"></div> Active Tumor
                        </div>
<div class="flex items-center gap-xs font-label-sm text-label-sm text-on-surface-variant">
<div class="w-3 h-3 rounded-sm border border-secondary border-dashed"></div> Edema
                        </div>
<div class="flex items-center gap-xs font-label-sm text-label-sm text-on-surface-variant">
<div class="w-3 h-3 rounded-sm bg-tertiary"></div> Necrosis
                        </div>
</div>
</div>
<!-- Current vs Baseline Bar Chart -->
<div class="col-span-4 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT flex flex-col">
<div class="p-md border-b border-outline-variant">
<h3 class="font-title-lg text-title-lg text-on-surface">Current vs Baseline</h3>
</div>
<div class="p-md flex-1 flex flex-col justify-around gap-md">
<!-- Bar Group 1 -->
<div>
<div class="flex justify-between font-label-sm text-label-sm text-on-surface-variant mb-xs">
<span>Active Tumor</span>
<span>15.9 / 15.9 cm³</span>
</div>
<div class="h-4 bg-surface-container rounded-sm overflow-hidden flex flex-col gap-px">
<div class="h-1/2 bg-primary-container" style="width: 60%"></div>
<div class="h-1/2 bg-outline" style="width: 60%"></div>
</div>
</div>
<!-- Bar Group 2 -->
<div>
<div class="flex justify-between font-label-sm text-label-sm text-on-surface-variant mb-xs">
<span>Edema</span>
<span>18.2 / 18.5 cm³</span>
</div>
<div class="h-4 bg-surface-container rounded-sm overflow-hidden flex flex-col gap-px">
<div class="h-1/2 bg-secondary" style="width: 70%"></div>
<div class="h-1/2 bg-outline" style="width: 72%"></div>
</div>
</div>
<!-- Bar Group 3 -->
<div>
<div class="flex justify-between font-label-sm text-label-sm text-on-surface-variant mb-xs">
<span>Necrosis</span>
<span>8.4 / 7.8 cm³</span>
</div>
<div class="h-4 bg-surface-container rounded-sm overflow-hidden flex flex-col gap-px">
<div class="h-1/2 bg-tertiary" style="width: 35%"></div>
<div class="h-1/2 bg-outline" style="width: 30%"></div>
</div>
</div>
<div class="mt-sm flex justify-start gap-md">
<div class="flex items-center gap-xs font-label-sm text-label-sm text-on-surface-variant">
<div class="w-3 h-3 rounded-sm bg-outline"></div> Baseline
                            </div>
<div class="flex items-center gap-xs font-label-sm text-label-sm text-on-surface-variant">
<div class="w-3 h-3 rounded-sm bg-surface-variant border border-outline"></div> Current
                            </div>
</div>
</div>
</div>
<!-- Tissue Classification Probabilities -->
<div class="col-span-12 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT mt-lg">
<div class="p-md border-b border-outline-variant">
<h3 class="font-title-lg text-title-lg text-on-surface">Tissue Classification Confidence</h3>
</div>
<div class="p-md">
<table class="w-full text-left border-collapse">
<thead>
<tr class="border-b border-surface-variant text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider">
<th class="pb-sm font-medium">Region</th>
<th class="pb-sm font-medium">Model Confidence</th>
<th class="pb-sm font-medium">Voxel Count</th>
<th class="pb-sm font-medium">Variance</th>
</tr>
</thead>
<tbody class="font-body-md text-body-md">
<tr class="border-b border-surface-variant hover:bg-surface-bright transition-colors">
<td class="py-sm py-md text-on-surface font-medium">Enhancing Tumor (ET)</td>
<td class="py-sm">
<div class="flex items-center gap-sm">
<span class="w-8">94%</span>
<div class="w-32 h-1 bg-surface-container rounded-full overflow-hidden">
<div class="h-full bg-primary-container" style="width: 94%"></div>
</div>
</div>
</td>
<td class="py-sm text-on-surface-variant">15,402</td>
<td class="py-sm text-on-surface-variant">±1.2%</td>
</tr>
<tr class="border-b border-surface-variant hover:bg-surface-bright transition-colors">
<td class="py-sm py-md text-on-surface font-medium">Peritumoral Edema (ED)</td>
<td class="py-sm">
<div class="flex items-center gap-sm">
<span class="w-8">88%</span>
<div class="w-32 h-1 bg-surface-container rounded-full overflow-hidden">
<div class="h-full bg-secondary" style="width: 88%"></div>
</div>
</div>
</td>
<td class="py-sm text-on-surface-variant">18,150</td>
<td class="py-sm text-on-surface-variant">±2.5%</td>
</tr>
<tr class="hover:bg-surface-bright transition-colors">
<td class="py-sm py-md text-on-surface font-medium">Necrotic Core (NCR)</td>
<td class="py-sm">
<div class="flex items-center gap-sm">
<span class="w-8">91%</span>
<div class="w-32 h-1 bg-surface-container rounded-full overflow-hidden">
<div class="h-full bg-tertiary" style="width: 91%"></div>
</div>
</div>
</td>
<td class="py-sm text-on-surface-variant">8,390</td>
<td class="py-sm text-on-surface-variant">±1.8%</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
</main>
</div>
</body></html>
```