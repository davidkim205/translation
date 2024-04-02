import gradio as gr
import pandas as pd

bleu_and_sbleu = pd.read_csv("assets/bleu_and_sbleu.csv")
bleu_by_src = pd.read_csv("assets/bleu_by_src.csv")
bleu_by_length = pd.read_csv("assets/bleu_by_length.csv")


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
            gr.Dataframe(value=bleu_and_sbleu, datatype="html")
            gr.Image(
                "assets/plot-bleu.png", show_download_button=False, container=False
            )
        with gr.Tab("bleu by src"):
            gr.Dataframe(value=bleu_by_src, datatype="html")
            gr.Image(
                "assets/plot-bleu-by-src.png",
                show_download_button=False,
                container=False,
            )
        with gr.Tab("bleu by sentence length"):
            gr.Dataframe(value=bleu_by_length, datatype="html")
            image = gr.Image(
                "assets/plot-bleu-by-sentence-length.png",
                show_download_button=False,
                container=False,
            )


demo.launch(share=True)
