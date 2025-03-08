import { Clock, MapPin } from "lucide-react";

import { Route } from "@/types";

export const TimeAndDistanceInfo = ({ route }: { route: Route }) => (
    <div className="grid grid-cols-2 gap-3">
        <div className="flex items-center gap-3 bg-blue-100/50 p-3 rounded-lg">
            <Clock className="w-6 h-6 text-blue-600" />
            <div>
                <p className="text-sm text-blue-600 font-medium">Tiempo estimado</p>
                <p className="text-xl font-bold text-blue-900">{route.estimated_time} minutos</p>
            </div>
        </div>
        <div className="flex items-center gap-3 bg-green-100/50 p-3 rounded-lg">
            <MapPin className="w-6 h-6 text-green-600" />
            <div>
                <p className="text-sm text-green-600 font-medium">Distancia total</p>
                <p className="text-xl font-bold text-green-900">{route.total_distance} km</p>
            </div>
        </div>
    </div>
);