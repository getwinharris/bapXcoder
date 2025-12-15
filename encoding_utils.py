def encode_content(content, encoding_type='utf-8'):
    """
    Encode content using various encoding schemes

    Function: Converts content between different text encoding formats (UTF-8, Base64, ASCII, Hex, etc.)
    Connection: Links to file processing and communication systems in the application
    Purpose: Handle international character sets and encoding transformations for diverse input
    Internal wiring: Connects to file operations, API communications, and user input processing
    Supported encodings: utf-8, ascii, base64, hex, unicode, and others
    """
    if encoding_type.lower() == 'base64':
        import base64
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        return base64.b64encode(content_bytes).decode('ascii')
    elif encoding_type.lower() == 'ascii':
        if isinstance(content, bytes):
            return content.decode('ascii', errors='ignore')
        return content.encode('ascii', errors='ignore').decode('ascii')
    elif encoding_type.lower() == 'unicode':
        if isinstance(content, str):
            return content
        return content.decode('utf-8', errors='replace')
    elif encoding_type.lower() == 'hex':
        if isinstance(content, str):
            return content.encode('utf-8').hex()
        return content.hex()
    elif encoding_type.lower() == 'utf-8':
        if isinstance(content, bytes):
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                # Try other common encodings if UTF-8 fails
                for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        return content.decode(enc)
                    except UnicodeDecodeError:
                        continue
                # If all fail, use utf-8 with error replacement
                return content.decode('utf-8', errors='replace')
        return content
    else:
        # Default to the specified encoding type
        if isinstance(content, bytes):
            try:
                return content.decode(encoding_type)
            except (UnicodeDecodeError, LookupError):
                return content.decode('utf-8', errors='replace')
        else:
            try:
                return content.encode(encoding_type).decode(encoding_type)
            except (UnicodeEncodeError, LookupError):
                return content


def decode_content(encoded_content, encoding_type='utf-8'):
    """
    Decode content from various encoding schemes

    Function: Converts encoded content back to readable format (UTF-8, Base64, ASCII, Hex, etc.)
    Connection: Links to content processing and display systems in the application
    Purpose: Handle international character sets and decoding transformations for diverse input
    Internal wiring: Connects to file readers, API response processors, and user input handlers
    Supported encodings: utf-8, ascii, base64, hex, unicode, and others
    """
    if encoding_type.lower() == 'base64':
        import base64
        if isinstance(encoded_content, str):
            encoded_bytes = encoded_content.encode('ascii')
        else:
            encoded_bytes = encoded_content
        return base64.b64decode(encoded_bytes).decode('utf-8', errors='replace')
    elif encoding_type.lower() == 'hex':
        if isinstance(encoded_content, str):
            return bytes.fromhex(encoded_content).decode('utf-8', errors='replace')
        return encoded_content.decode('utf-8', errors='replace')
    elif encoding_type.lower() in ['ascii', 'unicode', 'utf-8']:
        # For these encodings, just return the content as-is if it's already decoded
        if isinstance(encoded_content, bytes):
            return encoded_content.decode('utf-8', errors='replace')
        return encoded_content
    else:
        # For other encodings, try to decode
        if isinstance(encoded_content, bytes):
            try:
                return encoded_content.decode(encoding_type)
            except (UnicodeDecodeError, LookupError):
                return encoded_content.decode('utf-8', errors='replace')
        else:
            return encoded_content