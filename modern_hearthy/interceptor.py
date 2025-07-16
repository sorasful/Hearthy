"""
Modern network interceptor with async support
"""

import asyncio
import socket
import struct
from typing import Optional, Callable, Dict, Any, Tuple
import logging

from .types import PacketType, PacketData, PacketDirection, InterceptAction
from .protocol.splitter import ModernSplitter
from .protocol.decoder import decoder
from .battlegrounds.detector import BattlegroundsDetector
from .exceptions import InterceptError

logger = logging.getLogger(__name__)

class ModernInterceptor:
    """Modern network interceptor for Hearthstone"""
    
    def __init__(self, 
                 port: int = 1119,
                 host: str = "127.0.0.1",
                 battlegrounds_callback: Optional[Callable] = None) -> None:
        self.port = port
        self.host = host
        self.battlegrounds_detector = BattlegroundsDetector(battlegrounds_callback)
        self.packet_handlers: Dict[PacketType, Callable] = {}
        self.running = False
        
    def add_packet_handler(self, packet_type: PacketType, handler: Callable) -> None:
        """Add a handler for a specific packet type"""
        self.packet_handlers[packet_type] = handler
    
    async def start(self) -> None:
        """Start the interceptor"""
        self.running = True
        logger.info(f"Starting interceptor on {self.host}:{self.port}")
        
        server = await asyncio.start_server(
            self._handle_connection,
            self.host,
            self.port
        )
        
        async with server:
            await server.serve_forever()
    
    def stop(self) -> None:
        """Stop the interceptor"""
        self.running = False
        logger.info("Stopping interceptor")
    
    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle a new connection"""
        client_addr = writer.get_extra_info('peername')
        logger.info(f"New connection from {client_addr}")
        
        # Create connection to actual Hearthstone server
        try:
            # This would need to be configured for the actual Hearthstone server
            server_reader, server_writer = await asyncio.open_connection('127.0.0.1', 3724)
        except Exception as e:
            logger.error(f"Failed to connect to Hearthstone server: {e}")
            writer.close()
            return
        
        # Create splitters for both directions
        client_splitter = ModernSplitter()
        server_splitter = ModernSplitter()
        
        try:
            # Handle bidirectional communication
            await asyncio.gather(
                self._proxy_data(reader, server_writer, client_splitter, PacketDirection.CLIENT_TO_SERVER),
                self._proxy_data(server_reader, writer, server_splitter, PacketDirection.SERVER_TO_CLIENT)
            )
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            writer.close()
            server_writer.close()
            logger.info(f"Connection closed for {client_addr}")
    
    async def _proxy_data(self, 
                         reader: asyncio.StreamReader, 
                         writer: asyncio.StreamWriter,
                         splitter: ModernSplitter,
                         direction: PacketDirection) -> None:
        """Proxy data between client and server while intercepting packets"""
        
        while self.running:
            try:
                data = await reader.read(8192)
                if not data:
                    break
                
                # Process packets through splitter
                for packet_type, packet_data in splitter.feed(data):
                    action = await self._process_packet(packet_type, packet_data, direction)
                    
                    if action == InterceptAction.ACCEPT:
                        # Forward original packet
                        header = struct.pack('<II', packet_type, len(packet_data))
                        writer.write(header + packet_data)
                    elif action == InterceptAction.MODIFY:
                        # This would handle packet modification
                        pass
                    # REJECT means don't forward the packet
                
                await writer.drain()
                
            except Exception as e:
                logger.error(f"Error in proxy_data: {e}")
                break
    
    async def _process_packet(self, 
                            packet_type: PacketType, 
                            packet_data: PacketData,
                            direction: PacketDirection) -> InterceptAction:
        """Process an intercepted packet"""
        
        try:
            # Decode packet
            decoded = decoder.decode_packet(packet_type, packet_data)
            if decoded:
                # Process with Battlegrounds detector
                self.battlegrounds_detector.process_packet(packet_type, decoded.data, direction)
                
                # Call custom handlers
                handler = self.packet_handlers.get(packet_type)
                if handler:
                    return handler(decoded.data, direction)
            
            return InterceptAction.ACCEPT
            
        except Exception as e:
            logger.error(f"Error processing packet {packet_type}: {e}")
            return InterceptAction.ACCEPT