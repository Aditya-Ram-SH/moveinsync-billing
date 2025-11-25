import { useMutation } from "@tanstack/react-query";
import { useState, useRef } from "react";

import { api } from "../api/axios";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { useAuth } from "../context/AuthContext";

type UploadResult = {
  success: boolean;
  rowsIngested?: number;
  fileName?: string;
  fileSize?: number;
  message: string;
  timestamp?: Date;
};

export const TripsIngest = () => {
  const { user } = useAuth();
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const ingest = useMutation({
    mutationFn: (file: File) => api.ingestTrips(file),
    onSuccess: (response) => {
      const previous = Number(localStorage.getItem("ingestedTripCount") ?? 0);
      const pending = Number(localStorage.getItem("pendingTripCount") ?? 0);
      const newTotal = previous + response.rows_ingested;
      localStorage.setItem("ingestedTripCount", newTotal.toString());
      localStorage.setItem("pendingTripCount", (pending + response.rows_ingested).toString());
      
      setUploadResult({
        success: true,
        rowsIngested: response.rows_ingested,
        fileName: fileName || undefined,
        fileSize: fileSize || undefined,
        message: `Successfully imported ${response.rows_ingested} trip${response.rows_ingested !== 1 ? 's' : ''}`,
        timestamp: new Date(),
      });
      setFileName(null);
      setFileSize(null);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    onError: (error: any) => {
      setUploadResult({
        success: false,
        fileName: fileName || undefined,
        fileSize: fileSize || undefined,
        message: error?.response?.data?.detail ?? "Failed to ingest file. Please check the file format and try again.",
        timestamp: new Date(),
      });
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      setFileSize(file.size);
      setUploadResult(null);
      ingest.mutate(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file && file.type === "text/csv" || file.name.endsWith(".csv")) {
      setFileName(file.name);
      setFileSize(file.size);
      setUploadResult(null);
      ingest.mutate(file);
    } else {
      setUploadResult({
        success: false,
        message: "Please upload a CSV file",
        timestamp: new Date(),
      });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Trip Ingestion</h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload standardized CSV files to ingest trips into the system.
        </p>
      </div>

      {user?.role === "VENDOR" && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100">
                <svg
                  className="h-4 w-4 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-blue-900">Vendor Upload Notice</p>
                <p className="text-sm text-blue-700 mt-1">
                  As a vendor, you can only upload trips for your own vendor account. 
                  Make sure the <code className="bg-blue-100 px-1 rounded text-xs">vendor_id</code> in your CSV 
                  matches your vendor ID. All trips will be validated to ensure they belong to your vendor.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Upload CSV File</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <input
            ref={fileInputRef}
            id="trips-file-input"
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileChange}
          />
          
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`flex flex-col gap-4 rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
              isDragging
                ? "border-blue-500 bg-blue-50"
                : ingest.isPending
                ? "border-slate-300 bg-slate-50"
                : "border-slate-300 bg-white hover:border-slate-400"
            }`}
          >
            {ingest.isPending ? (
              <>
                <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600"></div>
                <div>
                  <p className="text-base font-semibold text-slate-700">Uploading...</p>
                  <p className="text-sm text-slate-500 mt-1">
                    Processing {fileName || "your file"}
                  </p>
                </div>
              </>
            ) : (
              <>
                <div className="mx-auto">
                  <svg
                    className="h-12 w-12 text-slate-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                </div>
                <div>
                  <p className="text-base font-semibold text-slate-700">
                    Drag and drop your CSV file here
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    or click the button below to browse
                  </p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="mx-auto"
                >
                  Choose File
                </Button>
                <p className="text-xs text-slate-400">
                  Accepted format: CSV (.csv)
                </p>
              </>
            )}
          </div>

          {fileName && !ingest.isPending && (
            <div className="rounded-md bg-slate-50 p-3">
              <p className="text-sm font-medium text-slate-700">Selected file:</p>
              <p className="text-sm text-slate-600">{fileName}</p>
              {fileSize && (
                <p className="text-xs text-slate-500 mt-1">
                  Size: {formatFileSize(fileSize)}
                </p>
              )}
            </div>
          )}

          {uploadResult && (
            <div
              className={`rounded-lg border-2 p-4 ${
                uploadResult.success
                  ? "border-green-200 bg-green-50"
                  : "border-red-200 bg-red-50"
              }`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                    uploadResult.success ? "bg-green-100" : "bg-red-100"
                  }`}
                >
                  {uploadResult.success ? (
                    <svg
                      className="h-5 w-5 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="h-5 w-5 text-red-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  )}
                </div>
                <div className="flex-1">
                  <p
                    className={`text-base font-semibold ${
                      uploadResult.success ? "text-green-800" : "text-red-800"
                    }`}
                  >
                    {uploadResult.success ? "Upload Successful!" : "Upload Failed"}
                  </p>
                  <p
                    className={`text-sm mt-1 ${
                      uploadResult.success ? "text-green-700" : "text-red-700"
                    }`}
                  >
                    {uploadResult.message}
                  </p>
                  {uploadResult.success && uploadResult.rowsIngested && (
                    <div className="mt-3 rounded-md bg-white p-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-slate-500">Trips Imported</p>
                          <p className="text-lg font-bold text-green-700">
                            {uploadResult.rowsIngested}
                          </p>
                        </div>
                        {uploadResult.fileSize && (
                          <div>
                            <p className="text-slate-500">File Size</p>
                            <p className="text-lg font-semibold text-slate-700">
                              {formatFileSize(uploadResult.fileSize)}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  {uploadResult.timestamp && (
                    <p className="text-xs text-slate-500 mt-2">
                      {formatTimestamp(uploadResult.timestamp)}
                    </p>
                  )}
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="mt-3"
                    onClick={() => {
                      setUploadResult(null);
                      setFileName(null);
                      setFileSize(null);
                      if (fileInputRef.current) {
                        fileInputRef.current.value = '';
                      }
                    }}
                  >
                    Upload Another File
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>CSV Format Requirements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div>
              <p className="font-semibold text-slate-700 mb-2">Required Columns:</p>
              <ul className="list-disc list-inside space-y-1 text-slate-600 ml-2">
                <li><code className="bg-slate-100 px-1 rounded">contract_id</code> - Contract ID</li>
                <li><code className="bg-slate-100 px-1 rounded">client_id</code> - Client ID</li>
                <li><code className="bg-slate-100 px-1 rounded">vendor_id</code> - Vendor ID</li>
                <li><code className="bg-slate-100 px-1 rounded">employee_id</code> - Employee ID</li>
                <li><code className="bg-slate-100 px-1 rounded">trip_type</code> - INBOUND/OUTBOUND/PICKUP/DROPOFF</li>
                <li><code className="bg-slate-100 px-1 rounded">booking_time</code> - Booking time (ISO format)</li>
                <li><code className="bg-slate-100 px-1 rounded">start_time</code> - Start time (ISO format)</li>
                <li><code className="bg-slate-100 px-1 rounded">end_time</code> - End time (ISO format)</li>
                <li><code className="bg-slate-100 px-1 rounded">distance_km</code> - Distance in kilometers</li>
                <li><code className="bg-slate-100 px-1 rounded">duration_min</code> - Duration in minutes</li>
                <li><code className="bg-slate-100 px-1 rounded">vehicle_type</code> - Vehicle type</li>
                <li><code className="bg-slate-100 px-1 rounded">vehicle_number</code> - Vehicle registration</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-slate-700 mb-2">Optional Columns:</p>
              <ul className="list-disc list-inside space-y-1 text-slate-600 ml-2">
                <li><code className="bg-slate-100 px-1 rounded">currency</code> - Currency code (default: INR)</li>
              </ul>
            </div>
            <div className="pt-2 border-t border-slate-200">
              <p className="text-xs text-slate-500">
                💡 Tip: Use the sample CSV file (<code className="bg-slate-100 px-1 rounded">backend/sample_trips.csv</code>) as a template.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </section>
  );
};

