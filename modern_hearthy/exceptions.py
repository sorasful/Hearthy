"""
Modern exception definitions
"""

class HearthyError(Exception):
    """Base exception for Hearthy errors"""
    pass

class DecodeError(HearthyError):
    """Error decoding packet data"""
    pass

class EncodeError(HearthyError):
    """Error encoding packet data"""
    pass

class BufferFullException(HearthyError):
    """Buffer overflow exception"""
    pass

class InterceptError(HearthyError):
    """Error in packet interception"""
    pass

class CardNotFound(HearthyError):
    """Card not found in database"""
    pass

class EntityNotFound(HearthyError):
    """Entity not found"""
    def __init__(self, entity_id: int):
        super().__init__(f'Could not find entity with id={entity_id}')
        self.entity_id = entity_id