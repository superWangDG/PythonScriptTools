
class ColorUtils:
    @staticmethod
    def hex_to_rgba(hex_color, alpha=1.0):
        if hex_color.startswith("#"):
            hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            raise ValueError("十六进制颜色值格式不正确，必须为6位，例如 '#3498db'")
        rgba = [int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        rgba.append(alpha)
        return rgba
