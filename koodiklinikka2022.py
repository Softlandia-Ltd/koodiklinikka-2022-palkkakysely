"""Analysis of Koodiklinikka 2022 salary dataset."""

import plotly.express as px
import pandas as pd
import streamlit as st

# Column names
COMPANY = "Työpaikka"
HOURS = "Työaika (jos työsuhteessa)"
SEX = "Sukupuoli"
EXPERIENCE = "Työkokemus"
SALARY = "Kuukausipalkka"
LOCATION = "Kaupunki"

# Define some constants for the names we need to fix
GOFORE = "gofore"
MAVERICKS = "mavericks"
SIILI = "siili"
VINCIT = "vincit"

st.title("Koodiklinikka 2022 palkkakysely")


@st.cache
def get_ytitle(normalized: bool):
    """Title for y-axis."""
    return "Osuus (%)" if normalized else "Lukumäärä (n)"


@st.cache
def load_data() -> pd.DataFrame:
    """Load the data and do light preprocessing."""
    df = pd.read_csv("data/koodiklinikka.csv")

    df[COMPANY] = df[COMPANY].str.lower()
    # remove leading and trailing spaces
    df[COMPANY] = df[COMPANY].str.rstrip(" ").str.lstrip(" ")
    # hardcoded fixes to correct company names spelled in different ways
    df.replace(
        {
            COMPANY: {
                "mavericks software oy": MAVERICKS,
                "mavericks software": MAVERICKS,
                "siili solutions oyj": SIILI,
                "siili solutions": SIILI,
                "gofore oyj": GOFORE,
                "vincit oyj": VINCIT,
            }
        },
        inplace=True,
    )
    df[COMPANY].iloc[df[COMPANY].isna()] = "-"

    df[LOCATION].iloc[df[LOCATION].isna()] = "-"

    df[SEX].iloc[~df[SEX].isin(["mies", "nainen"])] = "eos / muu"

    # drop rows where salary cannot be interpreted (easily)
    df[SALARY] = df[SALARY].str.replace(",", ".")
    df[SALARY] = df[SALARY].apply(pd.to_numeric, errors="coerce")
    df = df[df[SALARY].notna()]

    return df


with st.sidebar:

    st.image("assets/softlandia.png")
    st.header("Asetukset")
    norm = st.checkbox("Normalisoi prosenteiksi")
    binsize = st.slider("Bin-koko", min_value=100, max_value=1000, step=100, key="binz")

df = load_data()

st.header("Putsattu data")

st.write(
    "Alkuperäinen data Koodiklinikan [kyselystä](https://koodiklinikka.github.io/palkkakysely/2022/)."
)
st.write(
    """
    Putsasimme dataa ennen analyysiä. Korjasimme samaa tarkoittavat yhtiöiden
    nimet. Palkkana on käytetty ilmoitettuja kuukausituloja, eli muita tuloja
    ei tässä vaiheessa huomioida.
    """
)
st.write("Kevyesti putsattu data:")
st.dataframe(df)

# palkkajakauma per sukupuoli
st.header("Palkkajakaumat")
st.write(
    """
    Palkkajakauma sukupuolen mukaan.
    """
)
sex_dist_fig = px.histogram(
    df, x=SALARY, color=SEX, barmode="group", histnorm="percent" if norm else None
)
sex_dist_fig.update_traces(xbins=dict(size=binsize))
sex_dist_fig.update_layout(
    bargap=0.1, xaxis_title="Palkka", yaxis_title=get_ytitle(norm)
)
st.plotly_chart(sex_dist_fig, use_container_width=True)

st.write("Palkkajakauma yritysten mukaan")
company_filter = st.multiselect("Yritykset", options=sorted(df[COMPANY].unique()))
company_data = df[df[COMPANY].isin(company_filter)]
company_dist_fig = px.histogram(
    company_data,
    x=SALARY,
    color=COMPANY,
    barmode="group",
    histnorm="percent" if norm else None,
)
company_dist_fig.update_traces(xbins=dict(size=binsize))
company_dist_fig.update_layout(
    bargap=0.1, xaxis_title="Palkka", yaxis_title=get_ytitle(norm)
)
st.plotly_chart(company_dist_fig, use_container_width=True)

st.write(
    """
    Palkkajakauma sijainnin mukaan.
    """
)
location_filter = st.multiselect("Sijainti", options=sorted(df[LOCATION].unique()))
location_data = df[df[LOCATION].isin(location_filter)]
location_dist_fig = px.histogram(
    location_data,
    x=SALARY,
    color=LOCATION,
    barmode="group",
    histnorm="percent" if norm else None,
)
location_dist_fig.update_traces(xbins=dict(size=binsize))
location_dist_fig.update_layout(
    bargap=0.1, xaxis_title="Palkka", yaxis_title=get_ytitle(norm)
)
st.plotly_chart(location_dist_fig, use_container_width=True)

st.write("Työkokemuksen vaikutus")
hue = st.checkbox("Sukupuolen mukaan")
experience_fig = px.box(df, y=SALARY, x="Työkokemus", color=SEX if hue else None)
st.plotly_chart(experience_fig, use_container_width=True)

cols = st.columns(3)
with cols[1]:
    st.image("assets/softlandia.png")
    st.write(
        """
        App by [Softlandia](http://softlandia.fi/)
        """
    )
