import gradio as gr
import pandas as pd

from create_table import create


# 테이블 업데이트
def refresh():
    table1, table2, table3, table4 = create()
    return table1, table2, table3, table4


with gr.Blocks() as demo:
    # 테이블 초기화
    bleu_and_sbleu, bleu_by_domain, bleu_by_src, bleu_by_length = create()
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
                bleu_and_sbleu = gr.Dataframe(value=bleu_and_sbleu, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu.png",
                        show_download_button=False,
                        container=False,
                    )
        with gr.Tab("bleu by domain"):
            with gr.Group():
                bleu_by_domain = gr.Dataframe(value=bleu_by_domain, datatype="html")
                # with gr.Accordion("Show Chart", open=False):
                #     gr.Image(
                #         "assets/plot-bleu.png",
                #         show_download_button=False,
                #         container=False,
                #     )
        with gr.Tab("bleu by src"):
            with gr.Group():
                bleu_by_src = gr.Dataframe(value=bleu_by_src, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu-by-src.png",
                        show_download_button=False,
                        container=False,
                    )
        with gr.Tab("bleu by sentence length"):
            with gr.Group():
                bleu_by_length = gr.Dataframe(value=bleu_by_length, datatype="html")
                with gr.Accordion("Show Chart", open=False):
                    gr.Image(
                        "assets/plot-bleu-by-sentence-length.png",
                        show_download_button=False,
                        container=False,
                    )

    refresh_btn = gr.Button(value="Refresh")
    refresh_btn.click(refresh, outputs=[bleu_and_sbleu, bleu_by_domain, bleu_by_src, bleu_by_length])

demo.launch(server_name='0.0.0.0', share=True)
