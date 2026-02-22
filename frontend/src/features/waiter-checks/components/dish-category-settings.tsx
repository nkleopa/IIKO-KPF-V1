import { useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Settings, Loader2 } from "lucide-react";

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

  const { data: categories, isLoading } = useQuery({
    queryKey: ["dishCategories"],
    queryFn: () => api.getDishCategories(),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, fullness_category }: { id: number; fullness_category: string | null }) =>
      api.updateDishCategory(id, fullness_category),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dishCategories"] });
    },
  });

  const handleChange = (row: DishCategoryRow, value: string) => {
    const newCategory = value === "__null__" ? null : value;
    updateMutation.mutate({ id: row.id, fullness_category: newCategory });
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
      <PopoverContent align="end" className="w-[420px] p-0">
        <div className="px-4 py-3 border-b">
          <p className="text-sm font-medium">Категории блюд</p>
          <p className="text-xs text-muted-foreground mt-1">
            Идеальный чек: основное + доп. блюдо + напиток + десерт
          </p>
        </div>

        <div className="max-h-[60vh] overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : (
            sections.map((section) => (
              <div key={section.parent}>
                <div className="px-4 py-1.5 bg-muted/50 text-xs font-semibold text-muted-foreground sticky top-0">
                  {section.parent}
                </div>
                {section.items.map((row) => (
                  <div
                    key={row.id}
                    className="flex items-center justify-between gap-3 px-4 py-1.5 hover:bg-muted/30"
                  >
                    <span className="text-sm truncate min-w-0">{row.dish_group}</span>
                    <Select
                      value={row.fullness_category ?? "__null__"}
                      onValueChange={(v) => handleChange(row, v)}
                      disabled={updateMutation.isPending}
                    >
                      <SelectTrigger className="h-7 w-[140px] text-xs shrink-0">
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
                  </div>
                ))}
              </div>
            ))
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
