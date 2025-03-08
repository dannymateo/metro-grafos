
import { Chip } from "@nextui-org/react";
import { Train } from "lucide-react";

import { Route } from "@/types";

export const LinesInfo = ({ route }: { route: Route }) => (
    <div className="space-y-3">
        <div className="flex items-center gap-2">
            <Train className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-blue-900">Líneas del recorrido</span>
        </div>
        <div className="flex flex-wrap gap-2">
            {route.lines.map((line, index) => (
                <Chip key={index} variant="flat" color="primary">{line}</Chip>
            ))}
        </div>
    </div>
);