import {
    Card,
    CardHeader,
    CardBody,
    Table,
    TableHeader,
    TableColumn,
    TableBody,
    TableRow,
    TableCell,
    Button,
    Chip
} from "@nextui-org/react";
import { 
    History, 
    ArrowRight, 
    MapPin, 
    Navigation, 
    Clock, 
    Train, 
    Eye 
} from 'lucide-react';

import { useWebSocket } from '@/hooks/useWebSocket';
import { Props } from "./types";

export default function AdminPanel({ stations, onShowRoute }: Props) {
    const { routeHistory } = useWebSocket();

    if (!routeHistory?.length) {
        return null;
    }

    return (
        <Card className="shadow-sm">
            <CardHeader className="flex gap-3">
                <History className="w-4 h-4 md:w-5 md:h-5 text-[#2B3990]" />
                <div className="flex flex-col">
                    <p className="text-base md:text-lg font-semibold text-[#2B3990]">Historial de rutas</p>
                    <p className="text-xs md:text-sm text-gray-600">
                        Últimas rutas calculadas
                    </p>
                </div>
            </CardHeader>
            <CardBody className="px-2 md:px-6">
                <div className="overflow-x-auto -mx-2 md:mx-0">
                    <Table 
                        aria-label="Historial de rutas"
                        classNames={{
                            base: "min-w-full border-collapse",
                            th: "bg-gray-50 text-[#2B3990] font-medium",
                            td: "border-b border-gray-100"
                        }}
                        removeWrapper
                    >
                        <TableHeader>
                            <TableColumn className="text-xs md:text-sm whitespace-nowrap">
                                <div className="flex items-center gap-1">
                                    <MapPin className="w-3 h-3 hidden md:block" />
                                    <span>ORIGEN</span>
                                </div>
                            </TableColumn>
                            <TableColumn className="text-xs md:text-sm whitespace-nowrap">
                                <div className="flex items-center gap-1">
                                    <Navigation className="w-3 h-3 hidden md:block" />
                                    <span>DESTINO</span>
                                </div>
                            </TableColumn>
                            <TableColumn className="text-xs md:text-sm whitespace-nowrap">
                                <div className="flex items-center gap-1">
                                    <Clock className="w-3 h-3 hidden md:block" />
                                    <span>TIEMPO</span>
                                </div>
                            </TableColumn>
                            <TableColumn className="text-xs md:text-sm whitespace-nowrap">
                                <div className="flex items-center gap-1">
                                    <Train className="w-3 h-3 hidden md:block" />
                                    <span>LÍNEAS</span>
                                </div>
                            </TableColumn>
                            <TableColumn className="text-xs md:text-sm whitespace-nowrap">ACCIONES</TableColumn>
                        </TableHeader>
                        <TableBody>
                            {routeHistory.map((route, index) => (
                                <TableRow key={index} className="text-xs md:text-sm">
                                    <TableCell className="max-w-[100px] md:max-w-none truncate">
                                        <div className="flex items-center gap-1">
                                            <MapPin className="w-3 h-3 text-[#2B3990] hidden md:block" />
                                            <span className="truncate">{route.path[0]}</span>
                                        </div>
                                    </TableCell>
                                    <TableCell className="max-w-[100px] md:max-w-none truncate">
                                        <div className="flex items-center gap-1">
                                            <Navigation className="w-3 h-3 text-[#2B3990] hidden md:block" />
                                            <span className="truncate">{route.path[route.path.length - 1]}</span>
                                        </div>
                                    </TableCell>
                                    <TableCell className="whitespace-nowrap">
                                        <div className="flex items-center gap-1">
                                            <Clock className="w-3 h-3 text-[#2B3990] hidden md:block" />
                                            <span>{route.estimated_time} min</span>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex flex-wrap gap-1">
                                            {route.lines.map((line, i) => (
                                                <Chip 
                                                    key={i} 
                                                    size="sm" 
                                                    variant="flat"
                                                    className="bg-gray-100 text-[#2B3990] text-xs"
                                                    startContent={<Train className="w-2 h-2 hidden md:block" />}
                                                >
                                                    {line}
                                                </Chip>
                                            ))}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <Button
                                            size="sm"
                                            variant="flat"
                                            onPress={() => onShowRoute(route)}
                                            startContent={<Eye className="w-3 h-3" />}
                                            className="bg-[#2B3990] text-white hover:bg-[#232d73] transition-colors text-xs min-w-0 px-2 md:px-3"
                                        >
                                            <span className="hidden md:inline">Ver ruta</span>
                                            <span className="md:hidden">Ver</span>
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            </CardBody>
        </Card>
    );
} 