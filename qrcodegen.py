import streamlit as st
import qrcode
from PIL import Image
import io

# ---------- Streamlit Page Configuration ----------
st.set_page_config(page_title="QR Generator")  # Set page title for the app

# ---------- App Title ----------
st.title("QR Code Generator")

# ---------- User Input: Text or URL to Encode ----------
text = st.text_area("Text/Url to encode", placeholder="txt / url", height=120)

# ---------- Two Column Layout for QR Settings ----------
col1, col2 = st.columns(2)

with col1:
    # Size of each QR module (box)
    box_size = st.slider("Box Size (px/module)", 2, 20, 8)
    # Width of white border around QR code in modules
    border = st.slider("Border (Modules)", 0, 10, 4)

with col2:
    # QR error correction level options
    ec_choice = st.selectbox(
        "Error correction",
        ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
        index=1
    )
    # Final output image scale in pixels
    scale = st.slider("Output Scale (px)", 100, 1200, 480)

# ---------- Mapping Human-readable Labels to qrcode Constants ----------
ec_map = {
    "L (7%)": qrcode.constants.ERROR_CORRECT_L,
    "M (15%)": qrcode.constants.ERROR_CORRECT_M,
    "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
    "H (30%)": qrcode.constants.ERROR_CORRECT_H
}

# ---------- Button to Generate QR Code ----------
if st.button("Generate"):
    if not text.strip():
        st.error("Please enter text or a URL to encode.")  # Validation
    else:
        # Create QRCode object with chosen settings
        qr = qrcode.QRCode(
            error_correction=ec_map[ec_choice],
            box_size=box_size,
            border=border,
        )

        # Add the user text/URL to the QR code
        qr.add_data(text)
        qr.make(fit=True)

        # Create the QR image (black on white) and convert to RGB
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Resize QR image to match chosen scale while maintaining aspect ratio
        img_w, img_h = img.size
        factor = scale / max(img_w, img_h)
        new_size = (int(img_w * factor), int(img_h * factor))
        img = img.resize(new_size)

        # Display QR code in the app
        st.image(img, caption=text, use_column_width=False)

        # ---------- Download QR as PNG ----------
        buf = io.BytesIO()
        img.save(buf, format="PNG")  # Save image to memory buffer
        buf.seek(0)
        file_name = st.text_input("File name", value="qr_code")
        st.download_button(
            "Download PNG",
            data=buf,
            file_name=file_name + ".png",
            mime="image/png"
        )

        # ---------- Optional: Download as SVG ----------
        try:
            import qrcode.image.svg as svg
            factory = svg.SvgImage
            qr_svg = qrcode.make(text, image_factory=factory)
            svg_buf = io.BytesIO()
            qr_svg.save(svg_buf)
            svg_buf.seek(0)
            st.download_button(
                "Download SVG",
                data=svg_buf,
                file_name=file_name + ".svg",
                mime="image/svg+xml"
            )
        except Exception:
            # Ignore if SVG generation is unavailable
            pass
