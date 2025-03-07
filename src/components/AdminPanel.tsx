'use client';

import { useState, useEffect } from 'react';
import {
    Card,
    CardBody,
    CardHeader,
    Button,
    Select,
    SelectItem,
    Input,
    Table,
    TableHeader,
    TableColumn,
    TableBody,
    TableRow,
    TableCell,
    Chip
} from "@nextui-org/react";
import { AlertTriangle, CloudRain, Users } from 'lucide-react';

type AdminPanelProps = {
    stations: string[];
    onShowRoute?: (route: any) => void;
}

export default function AdminPanel({ stations, onShowRoute }: AdminPanelProps) {
    const [isMounted, setIsMounted] = useState(false);
    const [selectedStation, setSelectedStation] = useState("");
    const [reason, setReason] = useState("");
    const [closedStations, setClosedStations] = useState<string[]>([]);
    const [routeHistory, setRouteHistory] = useState<any[]>([]);
    
    useEffect(() => {
        setIsMounted(true);
        fetchAdminStatus();
        fetchRouteHistory();
        const interval = setInterval(fetchRouteHistory, 10000);
        return () => clearInterval(interval);
    }, []);

    const fetchAdminStatus = async () => {
        const res = await fetch('http://localhost:8000/admin/status');
        const data = await res.json();
        setClosedStations(data.closed_stations);
    };

    const fetchRouteHistory = async () => {
        const res = await fetch('http://localhost:8000/routes/history');
        const data = await res.json();
        setRouteHistory(data.routes);
    };

    const handleCloseStation = async () => {
        await fetch(`http://localhost:8000/admin/station/${selectedStation}/close?reason=${encodeURIComponent(reason)}`, {
            method: 'POST'
        });
        fetchAdminStatus();
    };

    const handleOpenStation = async (station: string) => {
        await fetch(`http://localhost:8000/admin/station/${station}/open`, {
            method: 'POST'
        });
        fetchAdminStatus();
    };

    // No renderizar nada hasta que el componente esté montado
    if (!isMounted) {
        return null;
    }

    return (
        <div className="space-y-6">
            <Card className="bg-white shadow-lg border-none">
                <CardHeader>
                    <h2 className="text-xl font-bold text-blue-900">Panel de Administración</h2>
                </CardHeader>
                <CardBody className="space-y-4">
                    <div className="flex gap-4">
                        <Select
                            label="Estación"
                            placeholder="Selecciona una estación"
                            value={selectedStation}
                            onChange={(e) => setSelectedStation(e.target.value)}
                        >
                            {stations.map((station) => (
                                <SelectItem key={station} value={station}>
                                    {station}
                                </SelectItem>
                            ))}
                        </Select>
                        <Input
                            label="Razón del cierre"
                            placeholder="Ej: Mantenimiento programado"
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                        />
                        <Button
                            color="danger"
                            onClick={handleCloseStation}
                            disabled={!selectedStation || !reason}
                        >
                            Cerrar Estación
                        </Button>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        {closedStations.map((station) => (
                            <Chip
                                key={station}
                                onClose={() => handleOpenStation(station)}
                                color="danger"
                                variant="flat"
                            >
                                {station}
                            </Chip>
                        ))}
                    </div>
                </CardBody>
            </Card>

            <Card className="bg-white shadow-lg border-none">
                <CardHeader>
                    <h2 className="text-xl font-bold text-blue-900">Historial de Rutas</h2>
                </CardHeader>
                <CardBody>
                    <Table aria-label="Historial de rutas">
                        <TableHeader>
                            <TableColumn>ID</TableColumn>
                            <TableColumn>Origen</TableColumn>
                            <TableColumn>Destino</TableColumn>
                            <TableColumn>Tiempo Est.</TableColumn>
                            <TableColumn>Estado</TableColumn>
                            <TableColumn>Acciones</TableColumn>
                        </TableHeader>
                        <TableBody>
                            {routeHistory.map((route) => (
                                <TableRow key={route.id}>
                                    <TableCell>{route.id}</TableCell>
                                    <TableCell>{route.path[0]}</TableCell>
                                    <TableCell>{route.path[route.path.length - 1]}</TableCell>
                                    <TableCell>{route.estimated_time} min</TableCell>
                                    <TableCell>
                                        <div className="flex gap-1">
                                            {(route.alerts || []).map((alert: string, i: number) => (
                                                <Chip
                                                    key={i}
                                                    size="sm"
                                                    startContent={
                                                        alert.includes('lluvia') ? <CloudRain className="w-3 h-3" /> :
                                                        alert.includes('congestión') ? <Users className="w-3 h-3" /> :
                                                        <AlertTriangle className="w-3 h-3" />
                                                    }
                                                    color={
                                                        alert.includes('lluvia') ? "primary" :
                                                        alert.includes('congestión') ? "warning" :
                                                        "danger"
                                                    }
                                                >
                                                    {alert}
                                                </Chip>
                                            ))}
                                            {(!route.alerts || route.alerts.length === 0) && (
                                                <Chip size="sm" color="success">Normal</Chip>
                                            )}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <Button
                                            size="sm"
                                            color="primary"
                                            variant="flat"
                                            onClick={() => onShowRoute?.(route)}
                                        >
                                            Ver en Mapa
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardBody>
            </Card>
        </div>
    );
} 