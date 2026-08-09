// Single frontend-side copy of validation policy. Duplicated from
// backend/app/config.py and backend/app/services/file_validation.py since
// frontend and backend are separate runtimes with no shared code.
//
// client side validation exists purely for immediate UX feedback

export const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];
export const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB

export const IMAGE_SOURCE_OPTIONS = [
  { value: "static_camera", label: "Static Camera" },
  { value: "drone", label: "Drone" },
  { value: "manual_upload", label: "Manual Upload" },
];

export const ANALYSIS_TYPE_OPTIONS = [
  { value: "classification", label: "Image Classification" },
  { value: "vehicle_detection", label: "Vehicle Detection" },
  { value: "image_quality", label: "Image Quality" },
];
