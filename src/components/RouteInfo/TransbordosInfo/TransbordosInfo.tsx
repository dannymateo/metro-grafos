import { Chip } from "@nextui-org/react";
import { GitCommit } from "lucide-react";

import { Route } from "@/types";

export const TransbordosInfo = ({ route }: { route: Route }) => (
    <div className="space-y-3">
        <div className="flex items-center gap-2">
            <GitCommit className="w-5 h-5 text-orange-500" />
            <span className="font-medium text-blue-900">Transbordos</span>
        </div>
        <div className="flex flex-wrap gap-2">
            {route.transbordos.map((transbordo, index) => (
                <Chip key={index} variant="flat" color="warning">{transbordo}</Chip>
            ))}
        </div>
    </div>
);