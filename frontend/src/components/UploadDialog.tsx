import { useRef, useState } from "react";

interface UploadDialogProps {
  open: boolean;
  onClose: () => void;
  onUpload: (file: File) => Promise<void>;
}

export function UploadDialog({ open, onClose, onUpload }: UploadDialogProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  return (
    <div className="dialog-backdrop" onClick={onClose}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <h2>Upload Document</h2>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            const file = fileRef.current?.files?.[0];
            if (!file) return;

            setUploading(true);
            setError(null);
            try {
              await onUpload(file);
              onClose();
            } catch (err) {
              setError(err instanceof Error ? err.message : "Upload failed");
            } finally {
              setUploading(false);
            }
          }}
        >
          <input ref={fileRef} type="file" required />
          {error && <p className="error">{error}</p>}
          <div className="dialog-actions">
            <button type="button" onClick={onClose} disabled={uploading}>
              Cancel
            </button>
            <button type="submit" disabled={uploading}>
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
