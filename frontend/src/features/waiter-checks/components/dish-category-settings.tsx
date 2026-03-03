import { useMemo, useState, useRef, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Settings, Loader2, ChevronRight, ChevronDown } from "lucide-react";

import { Button } from "@/components/ui/button";
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
import { Input } from "@/components/ui/input";
import { api, type DishCategoryRow } from "@/lib/api";

const CATEGORY_OPTIONS = [
  { value: "main", label: "Основное" },
  { value: "side", label: "Доп. блюдо" },
  { value: "drink", label: "Напиток" },
  { value: "dessert", label: "Десерт" },
  { value: "__null__", label: "Не учитывать" },
] as const;

function categoryLabel(cat: string | null): string {
  if (!cat) return "Не учитывать";
  const found = CATEGORY_OPTIONS.find((o) => o.value === cat);
  return found ? found.label : cat;
}

interface GroupSection {
  parent: string;
  items: DishCategoryRow[];
}

function groupByParent(categories: DishCategoryRow[]): GroupSection[] {
  const grouped = new Map<string, DishCategoryRow[]>();
  const uncategorized: DishCategoryRow[] = [];

  for (const cat of categories) {
    if (cat.parent_group) {
      const list = grouped.get(cat.parent_group);
      if (list) {
        list.push(cat);
      } else {
        grouped.set(cat.parent_group, [cat]);
      }
    } else {
      uncategorized.push(cat);
    }
  }

  const sections: GroupSection[] = [];
  const sortedParents = [...grouped.keys()].sort((a, b) => a.localeCompare(b));
  for (const parent of sortedParents) {
    sections.push({ parent, items: grouped.get(parent)! });
  }
  if (uncategorized.length > 0) {
    sections.push({ parent: "Прочее", items: uncategorized });
  }
  return sections;
}

export function DishCategorySettingsButton() {
  const queryClient = useQueryClient();
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const { data: categories, isLoading } = useQuery({
    queryKey: ["dishCategories"],
    queryFn: () => api.getDishCategories(),
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      fullness_category,
      fullness_weight,
    }: {
      id: number;
      fullness_category?: string | null;
      fullness_weight?: number;
    }) => api.updateDishCategory(id, fullness_category, fullness_weight),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dishCategories"] });
    },
  });

  const handleCategoryChange = (row: DishCategoryRow, value: string) => {
    const newCategory = value === "__null__" ? null : value;
    updateMutation.mutate({ id: row.id, fullness_category: newCategory });
  };

  const handleWeightSave = useCallback(
    (row: DishCategoryRow, value: string) => {
      const parsed = parseInt(value, 10);
      if (isNaN(parsed) || parsed < 1 || parsed > 10) return;
      if (parsed === row.fullness_weight) return;
      updateMutation.mutate({ id: row.id, fullness_weight: parsed });
    },
    [updateMutation],
  );

  const toggleSection = (parent: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(parent)) {
        next.delete(parent);
      } else {
        next.add(parent);
      }
      return next;
    });
  };

  const sections = useMemo(
    () => groupByParent(categories ?? []),
    [categories],
  );

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" title="Настройки категорий">
          <Settings className="h-4 w-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[520px] p-0">
        <div className="px-4 py-3 border-b">
          <p className="text-sm font-medium">Категории блюд</p>
          <p className="text-xs text-muted-foreground mt-1">
            Идеальный чек: сумма весов ≥ 4
          </p>
        </div>

        <div className="max-h-[60vh] overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : (
            sections.map((section) => {
              const isExpanded = expanded.has(section.parent);
              return (
                <div key={section.parent}>
                  <button
                    type="button"
                    onClick={() => toggleSection(section.parent)}
                    className="flex items-center gap-1.5 w-full px-4 py-1.5 bg-muted/50 text-xs font-semibold text-muted-foreground hover:bg-muted/80 sticky top-0"
                  >
                    {isExpanded ? (
                      <ChevronDown className="h-3.5 w-3.5 shrink-0" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5 shrink-0" />
                    )}
                    <span>{section.parent}</span>
                    <span className="ml-auto text-[10px] font-normal">
                      {section.items.length}
                    </span>
                  </button>
                  {isExpanded &&
                    section.items.map((row) => (
                      <DishGroupRow
                        key={row.id}
                        row={row}
                        onCategoryChange={handleCategoryChange}
                        onWeightSave={handleWeightSave}
                        disabled={updateMutation.isPending}
                      />
                    ))}
                </div>
              );
            })
          )}
        </div>

        {updateMutation.isSuccess && (
          <div className="px-4 py-2 border-t">
            <p className="text-xs text-green-600">
              Сохранено. Пересинхронизируйте для пересчёта.
            </p>
          </div>
        )}
        {updateMutation.isError && (
          <div className="px-4 py-2 border-t">
            <p className="text-xs text-red-600">Ошибка сохранения</p>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}

function DishGroupRow({
  row,
  onCategoryChange,
  onWeightSave,
  disabled,
}: {
  row: DishCategoryRow;
  onCategoryChange: (row: DishCategoryRow, value: string) => void;
  onWeightSave: (row: DishCategoryRow, value: string) => void;
  disabled: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      onWeightSave(row, e.currentTarget.value);
      e.currentTarget.blur();
    }
  };

  return (
    <div className="flex items-center gap-2 pl-8 pr-4 py-1.5 hover:bg-muted/30">
      <span className="text-sm truncate min-w-0 flex-1">{row.dish_group}</span>
      <Select
        value={row.fullness_category ?? "__null__"}
        onValueChange={(v) => onCategoryChange(row, v)}
        disabled={disabled}
      >
        <SelectTrigger className="h-7 w-[130px] text-xs shrink-0">
          <SelectValue>{categoryLabel(row.fullness_category)}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          {CATEGORY_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Input
        ref={inputRef}
        type="number"
        min={1}
        max={10}
        defaultValue={row.fullness_weight}
        className="h-7 w-[52px] text-xs text-center shrink-0"
        title="Вес наполняемости"
        disabled={disabled}
        onBlur={(e) => onWeightSave(row, e.currentTarget.value)}
        onKeyDown={handleKeyDown}
      />
    </div>
  );
}
