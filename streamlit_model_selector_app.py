import os
from datetime import datetime
from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st
import plotly.express as px

from model_selector_agent import run_model_selector, DEFAULT_LEADERBOARD_PATH



st.set_page_config(
    page_title="LLM Model Selector (LiveBench 기반)",
    page_icon="🧠",
    layout="wide",
)

if "leaderboard_path" not in st.session_state:
    st.session_state.leaderboard_path = DEFAULT_LEADERBOARD_PATH
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_user_query" not in st.session_state:
    st.session_state.last_user_query = ""
if "last_run_time" not in st.session_state:
    st.session_state.last_run_time = None


# ---------------------- 유틸 함수 ---------------------- #

def save_uploaded_file(uploaded_file) -> str | None:
    """업로드된 CSV 파일을 임시 경로에 저장"""
    try:
        suffix = Path(uploaded_file.name).suffix or ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            return tmp.name
    except Exception as e:
        st.error(f"파일 저장 중 오류 발생: {e}")
        return None


def load_leaderboard_preview(path: str, n_rows: int = 10) -> pd.DataFrame | None:
    """리더보드 CSV 일부(preview)를 DataFrame으로 로드"""
    try:
        df = pd.read_csv(path)
        return df.head(n_rows)
    except Exception as e:
        st.error(f"리더보드 CSV를 읽는 중 오류가 발생했습니다: {e}")
        return None


def build_topk_dataframe(result) -> pd.DataFrame:
    """ModelSelectorOutput.top_k를 pandas DataFrame으로 변환"""
    rows = []
    all_metric_keys: set[str] = set()

    for rec in result.top_k:
        all_metric_keys.update(rec.metrics.keys())

    all_metric_keys = sorted(all_metric_keys)

    for rec in result.top_k:
        row = {
            "rank": rec.rank,
            "model_name": rec.model_name,
            "composite_score": rec.composite_score,
        }
        for k in all_metric_keys:
            row[k] = rec.metrics.get(k, None)
        rows.append(row)

    df = pd.DataFrame(rows)
    return df



with st.sidebar:
    st.header("📊 LiveBench 리더보드 설정")

    st.markdown(
        """
LiveBench 리더보드 CSV를 사용해서  
태스크에 가장 적합한 LLM을 추천합니다.
"""
    )

    default_path = DEFAULT_LEADERBOARD_PATH
    if Path(default_path).exists():
        st.success(f"기본 리더보드 파일 감지: `{default_path}`")
    else:
        st.warning(f"기본 리더보드 파일을 찾을 수 없습니다: `{default_path}`")

    st.markdown("### 🔄 리더보드 CSV 업로드 (옵션)")
    uploaded_file = st.file_uploader(
        "LiveBench 리더보드 CSV 업로드 (미업로드 시 기본 파일 사용)",
        type=["csv"],
        help="download_data.py로 받은 livebench_leaderboard.csv를 그대로 업로드해도 됩니다.",
    )

    if uploaded_file is not None:
        saved_path = save_uploaded_file(uploaded_file)
        if saved_path:
            st.session_state.leaderboard_path = saved_path
            st.success(f"업로드된 리더보드를 사용합니다: `{saved_path}`")
    else:
        st.session_state.leaderboard_path = default_path

    st.markdown("---")
    st.markdown("**현재 사용 중인 리더보드 파일 경로:**")
    st.code(st.session_state.leaderboard_path or "(설정되지 않음)", language="bash")

    # 리더보드 미리보기
    if st.session_state.leaderboard_path and Path(st.session_state.leaderboard_path).exists():
        st.markdown("### 👀 리더보드 Preview")
        preview_df = load_leaderboard_preview(st.session_state.leaderboard_path)
        if preview_df is not None:
            st.dataframe(preview_df, use_container_width=True)
    else:
        st.info("리더보드 CSV가 존재하지 않습니다. download_data.py를 먼저 실행하거나 CSV를 업로드하세요.")



st.title("🧠 LLM Model Selector (LiveBench 기반)")
st.markdown(
    """
LiveBench 리더보드 + 태스크 설명을 기반으로  
여러 metric을 조합하여 **가장 적합한 LLM 모델**을 추천합니다.
"""
)

with st.expander("ℹ️ 이 도구가 하는 일", expanded=False):
    st.markdown(
        """
- LiveBench 리더보드 CSV를 기반으로 여러 모델의 성능을 비교합니다.
- 사용자가 원하는 **태스크 설명**을 입력하면:
  - 어떤 능력이 중요한지(예: math 정확도, reasoning, 설명력 등)를 해석하고
  - 리더보드 metric들을 조합해 **composite score**를 설계한 뒤
  - 가장 적합한 모델 1개 + 대안 모델 Top-k를 추천합니다.
- 예시 태스크:
  - `고등학생을 위한 수학 풀이/설명 tutor용 LLM`
  - `복잡한 코드 리뷰와 버그 설명을 잘하는 LLM`
  - `긴 문서를 요약하고 근거를 함께 제시하는 LLM`
"""
    )

st.markdown("---")

# 사용자 입력
st.subheader("💬 태스크 설명 입력")

user_query = st.text_area(
    "어떤 용도의 모델을 찾고 싶으신가요?",
    placeholder="예: 고등학생이 이해할 수 있는 수학 풀이와 단계별 해설을 잘해주는 LLM을 추천해줘.",
    height=120,
)

col_btn, col_dummy = st.columns([1, 3])

with col_btn:
    recommend_btn = st.button("🔍 모델 추천 받기", type="primary")


leaderboard_path = st.session_state.leaderboard_path

if recommend_btn:
    if not user_query.strip():
        st.error("태스크 설명을 먼저 입력해 주세요.")
    elif not leaderboard_path or not Path(leaderboard_path).exists():
        st.error(
            "리더보드 CSV 파일을 찾을 수 없습니다.\n"
            "download_data.py로 livebench_leaderboard.csv를 생성하거나, 사이드바에서 CSV를 업로드해 주세요."
        )
    else:
        with st.spinner("LiveBench 리더보드를 분석하여 최적의 모델을 찾고 있습니다..."):
            try:
                result = run_model_selector(
                    user_query=user_query.strip(),
                    leaderboard_path=leaderboard_path,
                )
                st.session_state.last_result = result
                st.session_state.last_user_query = user_query.strip()
                st.session_state.last_run_time = datetime.now()
                st.success("모델 추천이 완료되었습니다!")
            except Exception as e:
                st.error(f"모델 추천 중 오류가 발생했습니다: {e}")
                st.stop()


st.markdown("---")
st.header("📌 추천 결과")

result = st.session_state.last_result

if result is None:
    st.info("왼쪽에서 리더보드 설정을 확인한 뒤, 태스크 설명을 입력하고 **[모델 추천 받기]** 버튼을 눌러 주세요.")
else:
    # 상단 메타 정보
    meta_cols = st.columns(3)
    with meta_cols[0]:
        st.metric(
            "추천 기준 태스크",
            value=(st.session_state.last_user_query[:30] + "...")
            if len(st.session_state.last_user_query) > 30
            else st.session_state.last_user_query,
        )
    with meta_cols[1]:
        st.write("**리더보드 파일:**")
        st.code(st.session_state.leaderboard_path, language="bash")
    with meta_cols[2]:
        if st.session_state.last_run_time:
            st.write("**마지막 실행 시각:**")
            st.write(st.session_state.last_run_time.strftime("%Y-%m-%d %H:%M:%S"))

    st.markdown("---")

    st.subheader("🏆 Primary 추천 모델")

    primary = result.primary_model

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"### `{primary.model_name}`")
        st.markdown(
            f"""
- **Rank:** {primary.rank}
- **Composite Score:** `{primary.composite_score:.4f}`
"""
        )
    with c2:
        st.markdown("#### 사용된 가중치")
        if result.weights_used:
            weights_df = pd.DataFrame(
                [{"metric": k, "weight": v} for k, v in result.weights_used.items()]
            )
            st.dataframe(weights_df, hide_index=True, use_container_width=True)
        else:
            st.write("가중치 정보가 제공되지 않았습니다.")

    st.markdown("#### Primary 모델 세부 메트릭")
    if primary.metrics:
        primary_metrics_df = pd.DataFrame(
            [{"metric": k, "value": v} for k, v in primary.metrics.items()]
        )
        st.dataframe(primary_metrics_df, hide_index=True, use_container_width=True)
    else:
        st.info("Primary 모델의 개별 메트릭 정보가 없습니다.")

    st.markdown("---")

    #Top-k
    st.subheader("📈 Top-k 후보 모델")

    if result.top_k:
        topk_df = build_topk_dataframe(result)
        st.dataframe(topk_df, use_container_width=True)

        # 시각화 진행
        try:
            fig = px.bar(
                topk_df.sort_values("rank"),
                x="model_name",
                y="composite_score",
                color="rank",
                title="Top-k 모델 Composite Score 비교",
            )
            fig.update_layout(xaxis_title="Model", yaxis_title="Composite Score")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"그래프를 그리는 중 오류가 발생했습니다: {e}")
    else:
        st.info("Top-k 후보 모델 정보가 없습니다.")

    st.markdown("---")

    st.subheader("🧾 선택 이유 (Reasoning)")
    st.markdown(result.reasoning)

    with st.expander("🛠 Raw 결과(JSON) 보기", expanded=False):
        st.json(
            {
                "primary_model": result.primary_model.model_dump(),
                "top_k": [m.model_dump() for m in result.top_k],
                "weights_used": result.weights_used,
            }
        )


if __name__ == "__main__":
    pass
