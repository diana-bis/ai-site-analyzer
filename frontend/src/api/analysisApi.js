import client from "./client";

export function createAnalysis({
  siteName,
  captureDatetime,
  imageSource,
  analysisType,
  file,
}) {
  // Build a multipart/form-data request containing the image and metadata
  const formData = new FormData();
  formData.append("site_name", siteName);
  formData.append("capture_datetime", captureDatetime);
  formData.append("image_source", imageSource);
  formData.append("analysis_type", analysisType);
  formData.append("file", file);

  // Send the request to the backend to create a new analysis
  return client.post("/api/analysis", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
