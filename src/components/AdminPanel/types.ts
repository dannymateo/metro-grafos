import { Route } from "@/types";

export type Props = {
    stations: string[];
    onShowRoute: (route: Partial<Route>) => void;
}