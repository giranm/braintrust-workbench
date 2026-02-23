import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { Sun, Moon, Monitor, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Settings() {
  const [endpoint, setEndpoint] = useState("");
  const [saved, setSaved] = useState(false);
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    setEndpoint(localStorage.getItem("frappe-endpoint") || "");
  }, []);

  const handleSave = () => {
    localStorage.setItem("frappe-endpoint", endpoint);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const themeOptions = [
    { value: "light", icon: Sun, label: "Light" },
    { value: "dark", icon: Moon, label: "Dark" },
    { value: "system", icon: Monitor, label: "System" },
  ];

  return (
    <div className="container py-12 max-w-lg">
      <h1 className="text-2xl font-bold mb-8">Settings</h1>

      <div className="space-y-8">
        <div className="space-y-3">
          <Label htmlFor="endpoint" className="text-base font-medium">
            Frappe API Endpoint
          </Label>
          <p className="text-sm text-muted-foreground">
            The URL where support tickets will be posted.
          </p>
          <Input
            id="endpoint"
            placeholder="https://your-frappe-instance.com/api/method/..."
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
          />
          <Button onClick={handleSave} size="sm">
            {saved ? (
              <>
                <Check className="h-4 w-4 mr-1" /> Saved
              </>
            ) : (
              "Save"
            )}
          </Button>
        </div>

        <div className="space-y-3">
          <Label className="text-base font-medium">Theme</Label>
          <div className="flex gap-2">
            {themeOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setTheme(opt.value)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-colors",
                  theme === opt.value
                    ? "border-primary bg-primary/5 text-foreground"
                    : "border-border text-muted-foreground hover:text-foreground hover:bg-accent"
                )}
              >
                <opt.icon className="h-4 w-4" />
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
