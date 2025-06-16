import streamlit as st
# Add PyPDF2 import for PDF merging and splitting
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import io
# Add fitz (PyMuPDF) import for PDF compression and PDF to JPG
import fitz
# Add PIL and img2pdf for JPG to PDF
from PIL import Image
# Add os, tempfile, zipfile for file handling
import os
import tempfile
import zipfile
# Add platform for OS detection
import platform

# TitanPDF - Streamlit PDF Toolkit
# Initial UI Scaffolding

# Sidebar tool options
TOOLS = [
    "🏠 Home",
    "Merge PDF",
    "Split PDF",
    "Compress PDF",
    "Rotate PDF",
    "Word to PDF",
    "PDF to Word",
    "JPG to PDF",
    "PDF to JPG",
    "Add Watermark",
    "Add Page Numbers",
    "Protect PDF (Password)",
    "Unlock PDF (Remove Password)"
]

# Set Streamlit page config
st.set_page_config(
    page_title="TitanPDF - PDF Toolkit",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar for tool selection
st.sidebar.header("Select a Tool")
tool = st.sidebar.radio("Choose a PDF tool:", TOOLS)

# Home Screen
if tool == "🏠 Home":
    st.markdown("""
        <div style='text-align:center; padding-top: 30px; padding-bottom: 10px;'>
            <h1 style='font-size:3rem; font-weight:900;'>🦾 TitanPDF - Your PDF Wingman</h1>
        </div>
        <div style='text-align:center; font-size:1.3rem; padding-bottom: 20px;'>
            <b>Merge, split, rotate, convert, protect, watermark — all in one vibe.</b><br>
            Zero ads. Zero BS. 100% Free. 🛡️<br>
            For students, hustlers, and night-before-deadline warriors. 😵‍💫🔥
        </div>
        <div style='max-width: 600px; margin: 0 auto; padding: 20px 0 10px 0;'>
            <ul style='font-size:1.15rem; line-height:2;'>
                <li>🧩 <b>Merge PDF</b> — Combine files, easy peasy</li>
                <li>✂️ <b>Split PDF</b> — Break it up, page by page</li>
                <li>🗜️ <b>Compress PDF</b> — Shrink that file size</li>
                <li>🔄 <b>Rotate PDF</b> — Flip it how you want</li>
                <li>📝 <b>Word ↔️ PDF</b> — Convert both ways</li>
                <li>🖼️ <b>JPG ↔️ PDF</b> — Images to docs, docs to images</li>
                <li>💧 <b>Add Watermark</b> — Brand your pages</li>
                <li>🔢 <b>Add Page Numbers</b> — Stay organized</li>
                <li>🔒 <b>Protect PDF</b> — Lock it down</li>
                <li>🔓 <b>Unlock PDF</b> — Free your files</li>
            </ul>
        </div>
        <div style='text-align:center; font-size:1.2rem; padding: 20px 0 30px 0;'>
            👉 <b>Get Started:</b> Pick a tool from the sidebar and vibe with your PDFs!
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <div style='text-align:center; font-size:1.1rem; color: #888; padding-bottom: 10px;'>
            Built by Aditya 🔧
        </div>
    """, unsafe_allow_html=True)
else:
    # App title for all tools except Home
    st.title("🦾 TitanPDF - PDF Toolkit")
    st.markdown(f"## {tool}")

# --- Merge PDF Functionality ---
if tool == "Merge PDF":
    uploaded_files = st.file_uploader(
        "Upload PDF files to merge", type=["pdf"], accept_multiple_files=True
    )
    
    # Show warning if fewer than 2 PDFs are uploaded
    if uploaded_files is not None and len(uploaded_files) > 0:
        if len(uploaded_files) < 2:
            st.warning("Please upload at least 2 PDF files to merge.")
        else:
            # Button to trigger merge
            if st.button("Merge PDFs"):
                try:
                    with st.spinner("Merging PDFs..."):
                        merger = PdfMerger()
                        # Add each uploaded PDF in order
                        for pdf_file in uploaded_files:
                            merger.append(pdf_file)
                        # Output merged PDF to a BytesIO buffer
                        merged_pdf_bytes = io.BytesIO()
                        merger.write(merged_pdf_bytes)
                        merger.close()
                        merged_pdf_bytes.seek(0)
                    st.success("PDFs merged successfully!")
                    # Download button for merged PDF
                    st.download_button(
                        label="Download Merged PDF",
                        data=merged_pdf_bytes,
                        file_name="merged.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"An error occurred while merging PDFs: {e}")
    else:
        st.info("Upload two or more PDF files to merge them into one.")

# --- Split PDF Functionality ---
elif tool == "Split PDF":
    uploaded_file = st.file_uploader("Upload a PDF to split", type=["pdf"])
    if uploaded_file is not None:
        try:
            # Read the PDF to get number of pages
            pdf_reader = PdfReader(uploaded_file)
            num_pages = len(pdf_reader.pages)
            st.write(f"**Total pages:** {num_pages}")

            # Split mode selection
            split_mode = st.radio(
                "How do you want to split the PDF?",
                ("All Pages (each page as separate PDF)", "Custom Page Range")
            )

            if split_mode == "All Pages (each page as separate PDF)":
                if st.button("Split All Pages"):
                    with st.spinner("Splitting all pages..."):
                        download_links = []
                        for i in range(num_pages):
                            writer = PdfWriter()
                            writer.add_page(pdf_reader.pages[i])
                            output = io.BytesIO()
                            writer.write(output)
                            output.seek(0)
                            # Show download button for each page
                            st.download_button(
                                label=f"Download Page {i+1}",
                                data=output,
                                file_name=f"page_{i+1}.pdf",
                                mime="application/pdf"
                            )
                        st.success("All pages split successfully!")
            elif split_mode == "Custom Page Range":
                # Input for custom page range (1-based indexing)
                col1, col2 = st.columns(2)
                with col1:
                    start_page = st.number_input(
                        "Start Page", min_value=1, max_value=num_pages, value=1, step=1
                    )
                with col2:
                    end_page = st.number_input(
                        "End Page", min_value=1, max_value=num_pages, value=num_pages, step=1
                    )
                if st.button("Split Range"):
                    # Validate range
                    if start_page > end_page:
                        st.error("Start page cannot be after end page.")
                    else:
                        with st.spinner("Splitting selected page range..."):
                            try:
                                writer = PdfWriter()
                                for i in range(start_page-1, end_page):
                                    writer.add_page(pdf_reader.pages[i])
                                output = io.BytesIO()
                                writer.write(output)
                                output.seek(0)
                                st.download_button(
                                    label=f"Download Pages {start_page}-{end_page}",
                                    data=output,
                                    file_name=f"pages_{start_page}_to_{end_page}.pdf",
                                    mime="application/pdf"
                                )
                                st.success("Selected page range split successfully!")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")
    else:
        st.info("Upload a PDF file to split it into separate pages or a custom range.")

# --- Compress PDF Functionality ---
elif tool == "Compress PDF":
    uploaded_file = st.file_uploader("Upload a PDF to compress", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Compress PDF"):
            try:
                with st.spinner("Compressing PDF (reducing image resolution and cleaning metadata)..."):
                    # Load PDF with fitz (PyMuPDF)
                    pdf_bytes = uploaded_file.read()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

                    # Iterate through each page and each image, reduce image resolution
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        img_list = page.get_images(full=True)
                        for img_index, img in enumerate(img_list):
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            # Open image with PIL, resample, and re-insert
                            try:
                                from PIL import Image
                                import tempfile
                                img_ext = base_image["ext"]
                                with tempfile.NamedTemporaryFile(suffix=f".{img_ext}", delete=False) as tmp_img_file:
                                    tmp_img_file.write(image_bytes)
                                    tmp_img_file.flush()
                                    pil_img = Image.open(tmp_img_file.name)
                                    # Reduce DPI and size (downsample to 100dpi)
                                    pil_img = pil_img.convert("RGB")
                                    width, height = pil_img.size
                                    new_width = int(width * 100 / 300)  # assuming original 300dpi
                                    new_height = int(height * 100 / 300)
                                    pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
                                    # Save to bytes
                                    img_byte_arr = io.BytesIO()
                                    pil_img.save(img_byte_arr, format="JPEG", quality=70, optimize=True)
                                    img_byte_arr.seek(0)
                                    # Replace image in PDF
                                    page.replace_image(xref, img_byte_arr.read())
                            except Exception as e:
                                # If image processing fails, skip that image
                                continue
                    # Remove metadata
                    doc.set_metadata({})
                    # Save compressed PDF to buffer
                    compressed_pdf_bytes = io.BytesIO()
                    doc.save(compressed_pdf_bytes, garbage=4, deflate=True)
                    doc.close()
                    compressed_pdf_bytes.seek(0)
                st.success("PDF compressed successfully!")
                st.download_button(
                    label="Download Compressed PDF",
                    data=compressed_pdf_bytes,
                    file_name="compressed.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred during compression: {e}")
    else:
        st.info("Upload a PDF file to compress and optimize it.")

# --- Rotate PDF Functionality ---
elif tool == "Rotate PDF":
    uploaded_file = st.file_uploader("Upload a PDF to rotate pages", type=["pdf"])
    if uploaded_file is not None:
        # Let user select rotation angle
        angle = st.selectbox("Select rotation angle (degrees):", [90, 180, 270])
        if st.button("Rotate PDF"):
            try:
                with st.spinner("Rotating all pages..."):
                    # Read the PDF
                    pdf_reader = PdfReader(uploaded_file)
                    pdf_writer = PdfWriter()
                    # Rotate each page by the selected angle
                    for page in pdf_reader.pages:
                        page.rotate(angle)
                        pdf_writer.add_page(page)
                    # Write rotated PDF to buffer
                    rotated_pdf_bytes = io.BytesIO()
                    pdf_writer.write(rotated_pdf_bytes)
                    rotated_pdf_bytes.seek(0)
                st.success("PDF rotated successfully!")
                st.download_button(
                    label="Download Rotated PDF",
                    data=rotated_pdf_bytes,
                    file_name="rotated.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred while rotating the PDF: {e}")
    else:
        st.info("Upload a PDF file to rotate all its pages.")

# --- Word to PDF Functionality ---
elif tool == "Word to PDF":
    uploaded_file = st.file_uploader("Upload a Word document to convert to PDF", type=["docx", "doc"])
    if uploaded_file is not None:
        if st.button("Convert to PDF"):
            try:
                with st.spinner("Converting Word to PDF..."):
                    # Save uploaded file to a temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_word:
                        tmp_word.write(uploaded_file.read())
                        tmp_word.flush()
                        word_path = tmp_word.name
                    # Prepare output PDF path
                    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    pdf_path = tmp_pdf.name
                    tmp_pdf.close()
                    # Try docx2pdf (Windows only)
                    converted = False
                    if platform.system() == "Windows":
                        try:
                            from docx2pdf import convert
                            convert(word_path, pdf_path)
                            converted = True
                        except Exception as e:
                            st.warning(f"docx2pdf failed: {e}. Trying pypandoc...")
                    # Fallback to pypandoc (cross-platform)
                    if not converted:
                        try:
                            import pypandoc
                            pypandoc.convert_file(word_path, 'pdf', outputfile=pdf_path)
                            converted = True
                        except Exception as e:
                            st.error(f"Conversion failed: {e}")
                    if converted:
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        st.success("Word document converted to PDF!")
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name=os.path.splitext(uploaded_file.name)[0] + ".pdf",
                            mime="application/pdf"
                        )
                    # Clean up temp files
                    os.remove(word_path)
                    os.remove(pdf_path)
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
    else:
        st.info("Upload a Word (.docx or .doc) file to convert to PDF.")

# --- PDF to Word Functionality ---
elif tool == "PDF to Word":
    uploaded_file = st.file_uploader("Upload a PDF to convert to Word", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Convert to Word"):
            try:
                with st.spinner("Converting PDF to Word (.docx)..."):
                    # Save uploaded PDF to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                        tmp_pdf.write(uploaded_file.read())
                        tmp_pdf.flush()
                        pdf_path = tmp_pdf.name
                    # Prepare output docx path
                    tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
                    docx_path = tmp_docx.name
                    tmp_docx.close()
                    try:
                        from pdf2docx import Converter
                        cv = Converter(pdf_path)
                        cv.convert(docx_path, start=0, end=None)
                        cv.close()
                        with open(docx_path, "rb") as f:
                            docx_bytes = f.read()
                        st.success("PDF converted to Word (.docx)!")
                        st.download_button(
                            label="Download Word Document",
                            data=docx_bytes,
                            file_name=os.path.splitext(uploaded_file.name)[0] + ".docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
                    # Clean up temp files
                    os.remove(pdf_path)
                    os.remove(docx_path)
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
    else:
        st.info("Upload a PDF file to convert to Word (.docx).")

# --- JPG to PDF Functionality ---
elif tool == "JPG to PDF":
    uploaded_files = st.file_uploader("Upload JPG images to convert to PDF", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        # Let user reorder images
        filenames = [f.name for f in uploaded_files]
        order = st.multiselect(
            "Select image order (top to bottom):",
            filenames,
            default=filenames
        )
        # Map order to files
        ordered_files = [next(f for f in uploaded_files if f.name == fname) for fname in order]
        if st.button("Convert to PDF"):
            try:
                with st.spinner("Converting images to PDF..."):
                    image_list = []
                    for file in ordered_files:
                        img = Image.open(file).convert("RGB")
                        image_list.append(img)
                    # Save to PDF in memory
                    pdf_bytes = io.BytesIO()
                    if image_list:
                        image_list[0].save(pdf_bytes, format="PDF", save_all=True, append_images=image_list[1:])
                        pdf_bytes.seek(0)
                        st.success("Images converted to PDF!")
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name="images.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("No images to convert.")
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
    else:
        st.info("Upload one or more images to convert to a single PDF.")

# --- PDF to JPG Functionality ---
elif tool == "PDF to JPG":
    uploaded_file = st.file_uploader("Upload a PDF to convert to JPG images", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Convert to JPG"):
            try:
                with st.spinner("Converting PDF pages to JPG images..."):
                    # Read PDF with fitz
                    pdf_bytes = uploaded_file.read()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    image_buffers = []
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        pix = page.get_pixmap(dpi=200)
                        img_bytes = io.BytesIO(pix.tobytes("jpg"))
                        image_buffers.append((page_num+1, img_bytes))
                    if image_buffers:
                        st.success("PDF pages converted to JPG images!")
                        # Download links for each page
                        for page_num, img_bytes in image_buffers:
                            st.download_button(
                                label=f"Download Page {page_num} as JPG",
                                data=img_bytes,
                                file_name=f"page_{page_num}.jpg",
                                mime="image/jpeg"
                            )
                        # Optionally, offer bulk download as zip
                        if len(image_buffers) > 1:
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                                for page_num, img_bytes in image_buffers:
                                    zipf.writestr(f"page_{page_num}.jpg", img_bytes.getvalue())
                            zip_buffer.seek(0)
                            st.download_button(
                                label="Download All as ZIP",
                                data=zip_buffer,
                                file_name="pages.zip",
                                mime="application/zip"
                            )
                    else:
                        st.error("No images were generated from the PDF.")
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
    else:
        st.info("Upload a PDF file to convert its pages to JPG images.")

# --- Placeholders for other tools ---
elif tool == "Add Watermark":
    uploaded_file = st.file_uploader("Upload a PDF to add or remove a watermark", type=["pdf"])
    if uploaded_file is not None:
        # Radio for Add or Remove Watermark
        wm_action = st.radio("What do you want to do?", ("Add Watermark", "Remove Watermark"))
        if wm_action == "Add Watermark":
            # Watermark input options
            watermark_text = st.text_input("Watermark Text", value="TitanPDF")
            font_size = st.slider("Font Size", min_value=12, max_value=100, value=36)
            opacity = st.slider("Opacity", min_value=10, max_value=100, value=30, step=5)
            if st.button("Add Watermark"):
                if not watermark_text.strip():
                    st.error("Please enter watermark text.")
                else:
                    try:
                        with st.spinner("Adding watermark to all pages..."):
                            pdf_bytes = uploaded_file.read()
                            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            for page in doc:
                                # Calculate diagonal position
                                rect = page.rect
                                text = watermark_text
                                # Set watermark color (light gray)
                                color = (0.6, 0.6, 0.6)
                                # Add text as a single text span (for easier removal)
                                page.insert_textbox(
                                    rect,
                                    text,
                                    fontsize=font_size,
                                    color=color,
                                    rotate=0,
                                    overlay=True,
                                    fill_opacity=opacity/100.0,
                                    render_mode=3,  # Fill text
                                    fontname="helv"
                                )
                            # Save watermarked PDF
                            wm_pdf_bytes = io.BytesIO()
                            doc.save(wm_pdf_bytes)
                            doc.close()
                            wm_pdf_bytes.seek(0)
                        st.success("Watermark added!")
                        st.download_button(
                            label="Download Watermarked PDF",
                            data=wm_pdf_bytes,
                            file_name="watermarked.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"An error occurred while adding watermark: {e}")
        elif wm_action == "Remove Watermark":
            st.info("This will attempt to remove watermarks added by this tool (same text, font, and color).")
            if st.button("Remove Watermark"):
                try:
                    with st.spinner("Attempting to remove watermark from all pages..."):
                        pdf_bytes = uploaded_file.read()
                        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                        watermark_found = False
                        for page in doc:
                            # Extract all text spans
                            text_instances = page.get_text("dict")
                            blocks = text_instances.get("blocks", [])
                            for b in blocks:
                                if b.get("type") == 0:  # text block
                                    for line in b.get("lines", []):
                                        for span in line.get("spans", []):
                                            # Heuristic: look for light gray, rotated, Helvetica, and large font
                                            if (
                                                span.get("font", "").lower().startswith("helv") and
                                                span.get("color", 0) == 10066329 and  # 0x999999 in decimal
                                                span.get("size", 0) >= 12 and
                                                abs(span.get("origin")[0] - span.get("origin")[1]) > 0 and
                                                span.get("text", "").strip() != ""
                                            ):
                                                # Remove this span by redacting its bbox
                                                page.add_redact_annot(span["bbox"], fill=(1, 1, 1))
                                                watermark_found = True
                            if watermark_found:
                                page.apply_redactions()
                        if watermark_found:
                            clean_pdf_bytes = io.BytesIO()
                            doc.save(clean_pdf_bytes)
                            doc.close()
                            clean_pdf_bytes.seek(0)
                            st.success("Watermark removed!")
                            st.download_button(
                                label="Download Clean PDF",
                                data=clean_pdf_bytes,
                                file_name="no_watermark.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Watermark not detected or cannot be removed safely.")
                except Exception as e:
                    st.error(f"An error occurred while removing watermark: {e}")
    else:
        st.info("Upload a PDF to add or remove a watermark.")
elif tool == "Add Page Numbers":
    uploaded_file = st.file_uploader("Upload a PDF to add page numbers", type=["pdf"])
    if uploaded_file is not None:
        # Font size slider
        font_size = st.slider("Font Size", min_value=8, max_value=48, value=14)
        # Page number position
        position = st.selectbox(
            "Page Number Position:",
            ["Bottom-Right", "Bottom-Center", "Bottom-Left"],
            index=0
        )
        if st.button("Add Page Numbers"):
            try:
                with st.spinner("Adding page numbers to all pages..."):
                    pdf_bytes = uploaded_file.read()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    margin = 36  # 0.5 inch margin
                    for i, page in enumerate(doc):
                        page_num = i + 1
                        text = str(page_num)
                        rect = page.rect
                        # Calculate position
                        y = rect.height - margin
                        if position == "Bottom-Right":
                            x = rect.width - margin
                            align = 2  # right
                        elif position == "Bottom-Center":
                            x = rect.width / 2
                            align = 1  # center
                        else:  # Bottom-Left
                            x = margin
                            align = 0  # left
                        # Add page number
                        page.insert_text(
                            (x, y),
                            text,
                            fontsize=font_size,
                            color=(0, 0, 0),
                            fontname="helv",
                            render_mode=0,
                            rotate=0,
                            align=align
                        )
                    # Save PDF with page numbers
                    numbered_pdf_bytes = io.BytesIO()
                    doc.save(numbered_pdf_bytes)
                    doc.close()
                    numbered_pdf_bytes.seek(0)
                st.success("Page numbers added!")
                st.download_button(
                    label="Download PDF with Page Numbers",
                    data=numbered_pdf_bytes,
                    file_name="page_numbers.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred while adding page numbers: {e}")
    else:
        st.info("Upload a PDF to add page numbers.")
elif tool == "Protect PDF (Password)":
    uploaded_file = st.file_uploader("Upload a PDF to protect with a password", type=["pdf"])
    password = st.text_input("Enter password to protect PDF", type="password")
    if uploaded_file is not None:
        if st.button("Protect PDF"):
            if not password:
                st.error("Please enter a password.")
            else:
                try:
                    with st.spinner("Encrypting PDF with password..."):
                        pdf_reader = PdfReader(uploaded_file)
                        pdf_writer = PdfWriter()
                        for page in pdf_reader.pages:
                            pdf_writer.add_page(page)
                        pdf_writer.encrypt(password)
                        protected_pdf_bytes = io.BytesIO()
                        pdf_writer.write(protected_pdf_bytes)
                        protected_pdf_bytes.seek(0)
                    st.success("PDF protected with password!")
                    st.download_button(
                        label="Download Protected PDF",
                        data=protected_pdf_bytes,
                        file_name="protected.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"An error occurred while protecting the PDF: {e}")
    else:
        st.info("Upload a PDF and enter a password to protect it.")
elif tool == "Unlock PDF (Remove Password)":
    uploaded_file = st.file_uploader("Upload a password-protected PDF to unlock", type=["pdf"])
    password = st.text_input("Enter password to unlock PDF", type="password")
    if uploaded_file is not None:
        if st.button("Unlock PDF"):
            if not password:
                st.error("Please enter the password.")
            else:
                try:
                    with st.spinner("Unlocking PDF..."):
                        pdf_reader = PdfReader(uploaded_file)
                        # Try to decrypt with the provided password
                        if pdf_reader.is_encrypted:
                            if not pdf_reader.decrypt(password):
                                st.error("Incorrect password or unable to decrypt PDF.")
                            else:
                                pdf_writer = PdfWriter()
                                for page in pdf_reader.pages:
                                    pdf_writer.add_page(page)
                                # Write out the unlocked PDF
                                unlocked_pdf_bytes = io.BytesIO()
                                pdf_writer.write(unlocked_pdf_bytes)
                                unlocked_pdf_bytes.seek(0)
                                st.success("PDF unlocked!")
                                st.download_button(
                                    label="Download Unlocked PDF",
                                    data=unlocked_pdf_bytes,
                                    file_name="unlocked.pdf",
                                    mime="application/pdf"
                                )
                        else:
                            pdf_writer = PdfWriter()
                            for page in pdf_reader.pages:
                                pdf_writer.add_page(page)
                            unlocked_pdf_bytes = io.BytesIO()
                            pdf_writer.write(unlocked_pdf_bytes)
                            unlocked_pdf_bytes.seek(0)
                            st.success("PDF unlocked!")
                            st.download_button(
                                label="Download Unlocked PDF",
                                data=unlocked_pdf_bytes,
                                file_name="unlocked.pdf",
                                mime="application/pdf"
                            )
                except Exception as e:
                    st.error(f"An error occurred while unlocking the PDF: {e}")
    else:
        st.info("Upload a password-protected PDF and enter the password to unlock it.")

# Footer
st.markdown("---")
st.markdown("<center>Made with ❤️ By goblinasaddy | TitanPDF MVP</center>", unsafe_allow_html=True) 