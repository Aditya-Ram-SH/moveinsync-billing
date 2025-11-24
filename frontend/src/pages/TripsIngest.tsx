import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { api } from "../api/axios";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export const TripsIngest = () => {
  const [fileName, setFileName] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("");

  const ingest = useMutation({
    mutationFn: (file: File) => api.ingestTrips(file),
    onSuccess: (response) => {
      const previous = Number(localStorage.getItem("ingestedTripCount") ?? 0);
      const pending = Number(localStorage.getItem("pendingTripCount") ?? 0);
      const newTotal = previous + response.rows_ingested;
      localStorage.setItem("ingestedTripCount", newTotal.toString());
      localStorage.setItem("pendingTripCount", (pending + response.rows_ingested).toString());
      setMessage(`Imported ${response.rows_ingested} rows successfully`);
      setFileName(null);
    },
    onError: (error: any) => {
      setMessage(error?.response?.data?.detail ?? "Failed to ingest file");
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      ingest.mutate(file);
    }
  };

  return (
    <section className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Trip Ingestion</h1>
        <p className="text-sm text-slate-500">Upload standardized CSV files to ingest trips.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Upload CSV</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <input
            id="trips-file-input"
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileChange}
          />
          <div className="flex flex-col gap-2 rounded-md border border-dashed border-slate-300 p-6 text-center">
            <p className="text-sm text-slate-600">
              Drag and drop your trip CSV or click the button to select a file.
            </p>
            <Button
              type="button"
              variant="outline"
              onClick={() => document.getElementById("trips-file-input")?.click()}
              disabled={ingest.isPending}
            >
              {ingest.isPending ? "Uploading..." : "Choose File"}
            </Button>
            {fileName && <p className="text-xs text-slate-500">{fileName}</p>}
          </div>
          {message && <p className="text-sm text-slate-600">{message}</p>}
        </CardContent>
      </Card>
    </section>
  );
};

