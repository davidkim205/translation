import gradio as gr
import pandas as pd

from create_table import create


# 테이블 업데이트
def refresh():
    table1, table2, table3 = create()
    return table1, table2, table3


with gr.Blocks() as demo:
    # 테이블 초기화
    table1, table2, table3 = create()
    with gr.Row():
        gr.Markdown(
            """
            # 🏆 Iris Translation Leaderboard
            Iris Translation is a project designed to evaluate Korean-to-English translation models
            
            ## github
            - https://github.com/davidkim205/translation

            ## How to add model
            If you want to add a new model, please write the model name and template in the [github issue](https://github.com/davidkim205/translation/issues).

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
                table1 = gr.Dataframe(value=table1, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu.png",
                        show_download_button=False,
                        container=False,
                    )
        with gr.Tab("bleu by src"):
            with gr.Group():
                table2 = gr.Dataframe(value=table2, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu-by-src.png",
                        show_download_button=False,
                        container=False,
                    )
        with gr.Tab("bleu by sentence length"):
            with gr.Group():
                table3 = gr.Dataframe(value=table3, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu-by-sentence-length.png",
                        show_download_button=False,
                        container=False,
                    )

    refresh_btn = gr.Button(value="Refresh")
    refresh_btn.click(refresh, outputs=[table1, table2, table3])

demo.launch(server_name='0.0.0.0', share=True)
