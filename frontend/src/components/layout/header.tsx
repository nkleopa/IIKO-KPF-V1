import { format } from "date-fns";
import { ru } from "date-fns/locale";
import { CalendarIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { BranchInfo } from "@/lib/api";

interface HeaderProps {
  branches: BranchInfo[];
  selectedBranchId: number;
  onBranchChange: (id: number) => void;
  dateFrom: Date;
  dateTo: Date;
  onDateFromChange: (d: Date) => void;
  onDateToChange: (d: Date) => void;
}

function DatePicker({
  date,
  onSelect,
  label,
}: {
  date: Date;
  onSelect: (d: Date) => void;
  label: string;
}) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-[160px] justify-start text-left font-normal",
            !date && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, "dd.MM.yyyy") : label}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={date}
          onSelect={(d) => d && onSelect(d)}
          locale={ru}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  );
}

export function Header({
  branches,
  selectedBranchId,
  onBranchChange,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
}: HeaderProps) {
  return (
    <header className="border-b bg-white px-6 py-4">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-semibold tracking-tight">KPF Dashboard</h1>
          <Select
            value={String(selectedBranchId)}
            onValueChange={(v) => onBranchChange(Number(v))}
          >
            <SelectTrigger className="w-[280px]">
              <SelectValue placeholder="Филиал" />
            </SelectTrigger>
            <SelectContent>
              {branches.map((b) => (
                <SelectItem key={b.id} value={String(b.id)}>
                  {b.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <DatePicker date={dateFrom} onSelect={onDateFromChange} label="С" />
          <span className="text-muted-foreground">—</span>
          <DatePicker date={dateTo} onSelect={onDateToChange} label="По" />
        </div>
      </div>
    </header>
  );
}
