import gradio as gr
import pandas as pd
from create_table import create

# 테이블 동적 생성
bleu_and_sbleu, bleu_by_src, bleu_by_length = create()


# 테이블 업데이트
def refresh():
    return create()


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown(
            """
            # 🏆 Iris Translation Leaderboard
            Iris Translation is a project designed to evaluate Korean-to-English translation models
            
            [GitHub](https://github.com/davidkim205/translation)

            ## evaluation criteria
            - **Bleu**: average bleu score
            - **SBleu**: Self-Bleu(double translation evaluation)
            - **Bleu-SL**: bleu by sentence length
            - **Duplicate**: count of repetitive sentence generation
            - **Length Exceeds**: count of mismatches in translated sentence lengths exceeding the threshold
            """
        )
    with gr.Row():
        with gr.Tab("bleu and sbleu"):
            with gr.Group():
                table1 = gr.Dataframe(value=bleu_and_sbleu, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu.png",
                        show_download_button=False,
                        container=False,
                    )
        with gr.Tab("bleu by src"):
            with gr.Group():
                table2 = gr.Dataframe(value=bleu_by_src, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu-by-src.png",
                        show_download_button=False,
                        container=False,
                    )
        with gr.Tab("bleu by sentence length"):
            with gr.Group():
                table3 = gr.Dataframe(value=bleu_by_length, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu-by-sentence-length.png",
                        show_download_button=False,
                        container=False,
                    )
    refresh_btn = gr.Button(value="Refresh")
    refresh_btn.click(refresh, outputs=[table1, table2, table3])

demo.launch(share=True)
