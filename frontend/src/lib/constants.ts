export function fmtMoney(value: string): string {
  return `$${value}`;
}

export function fmtNumber(value: number): string {
  return value.toLocaleString("es-EC");
}

export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export const TYPOLOGIES = [
  { code: "hospital", name: "Hospitalaria / crítica", description: "Quirófanos, aislamiento y UCI.", icon: "local_hospital" },
  { code: "institucion_educativa", name: "Educativa", description: "Escuelas, universidades y guarderías.", icon: "school" },
  { code: "oficina", name: "Corporativa / oficina", description: "Sedes administrativas y comerciales.", icon: "corporate_fare" },
  { code: "industria", name: "Industrial / logística", description: "Almacenes y líneas de manufactura.", icon: "precision_manufacturing" },
] as const;

export const INFRASTRUCTURE_LABELS: Record<string, string> = {
  hospital: "Hospital",
  oficina: "Oficina",
  centro_comercial: "Centro comercial",
  institucion_educativa: "Institución educativa",
  industria: "Industria",
  otro: "Otro",
};
