import { useState } from "react";
import { subDays, format } from "date-fns";

export function useDateRange() {
  const [dateFrom, setDateFrom] = useState<Date>(subDays(new Date(), 7));
  const [dateTo, setDateTo] = useState<Date>(subDays(new Date(), 1));

  return {
    dateFrom,
    dateTo,
    setDateFrom,
    setDateTo,
    dateFromStr: format(dateFrom, "yyyy-MM-dd"),
    dateToStr: format(dateTo, "yyyy-MM-dd"),
  };
}
