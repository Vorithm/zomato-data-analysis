import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

st.set_page_config(page_title="Zomato Data Dashboard", layout="wide")
st.title("📊 Zomato Restaurant Data Dashboard")

# Sidebar: Zoom controls
st.sidebar.header("🔍 Zoom Controls")
zoom_level = st.sidebar.radio("Select Zoom Level", ["Very Small", "Small", "Medium", "Large"], index=1)
zoom_map = {
    "Very Small": (3, 2),
    "Small": (5, 3),
    "Medium": (8, 5),
    "Large": (12, 7)
}
figsize = zoom_map[zoom_level]

# Session state logic for remembering sample data usage
if "use_sample" not in st.session_state:
    st.session_state.use_sample = False

# File uploader and sample button
uploaded_file = st.file_uploader("Upload your Zomato dataset (CSV)", type=["csv"])
sample_button = st.button("Use Sample Zomato Data")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.use_sample = False
    st.success("File uploaded successfully!")
elif sample_button:
    df = pd.read_csv("uploaded_data.csv")
    st.session_state.use_sample = True
    st.success("Sample dataset loaded successfully!")
elif st.session_state.use_sample:
    df = pd.read_csv("uploaded_data.csv")
else:
    st.warning("Please upload a Zomato-style CSV file to get started or click 'Use Sample Zomato Data'.")
    st.stop()

# === All existing functionality remains below ===

st.subheader("Preview of Dataset")

if 'link' in df.columns:
    preview_df = df.head(10).copy()
    preview_df['Menu Link'] = preview_df['link'].apply(
        lambda x: f"<a href='{x.rstrip('/')}/menu' target='_blank'>📄 View Menu</a>" if pd.notnull(x) else 'N/A'
    )
    st.write(preview_df[['rest_name', 'loc', 'dine_rating', 'Cost (RS)', 'Menu Link']].to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.dataframe(df.head(10))

# ✅ Project Explanation (New Section)
    st.markdown("### 🧠 What's This Dashboard All About?")
    st.markdown("""
    Welcome to your personal food intelligence dashboard! 🍽  
    This analysis dives deep into Zomato’s restaurant data from Pune to reveal:

    - ⭐ How diners and delivery users rate their experiences  
    - 📍 Which neighborhoods are foodie magnets  
    - 🍛 What cuisines dominate the local taste buds  
    - 💸 How restaurant types impact pricing  
    - 🔍 Where high ratings meet low costs for hidden gems  

    Whether you're a curious customer, a restaurant owner, or a data enthusiast, this dashboard helps you discover patterns behind the plates!  
    So sit tight, sip your chai, and let's decode Pune’s culinary code together. ☕📊
    """)

st.subheader("📌 Basic Information")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Restaurants", len(df))
    st.metric("Unique Locations", df['loc'].nunique() if 'loc' in df else 0)
with col2:
    st.metric("Unique Cuisines", df['cuisine'].nunique() if 'cuisine' in df else 0)
    st.metric("Max Cost", f"Rs. {df['Cost (RS)'].max():,.0f}" if 'Cost (RS)' in df else "N/A")
with col3:
    st.metric("City", "Pune")

st.subheader("⭐ Dine & Delivery Ratings Distribution")
col3, col4 = st.columns(2)
with col3:
    if 'dine_rating' in df:
        fig2, ax2 = plt.subplots(figsize=figsize)
        sns.histplot(df['dine_rating'].dropna(), bins=10, kde=True, ax=ax2, color='skyblue')
        ax2.set_title("Dine Rating Distribution")
        st.pyplot(fig2)
        avg_dine = df['dine_rating'].mean()
        st.markdown(f"""
        <div style="background-color:#e8f4fd;padding:15px;border-radius:10px">
        🎯 <b>Insightful Observation:</b><br><br>
        On analyzing the dine-in rating distribution, we observe that the average rating given by customers is <b>{avg_dine:.2f} stars</b> 🌟.<br><br>
        This suggests that diners in Pune generally enjoy positive in-house restaurant experiences. The smooth KDE curve indicates that ratings are mostly clustered around the mid to high range, reflecting a relatively consistent customer satisfaction level.<br><br>
        ⭐ <i>This could imply that the city offers a solid dine-in culture with good ambiance, service, and food quality — making dining out a pleasant experience for most patrons.</i><br><br>
        📌 <b>Tip:</b> Restaurants with consistently higher dine-in ratings can be promoted as "Top Dine-Out Spots in Pune" to attract more footfall!
        </div>
        """, unsafe_allow_html=True)
with col4:
    if 'delivery_rating' in df:
        fig3, ax3 = plt.subplots(figsize=figsize)
        sns.histplot(df['delivery_rating'].dropna(), bins=10, kde=True, ax=ax3, color='salmon')
        ax3.set_title("Delivery Rating Distribution")
        st.pyplot(fig3)
        avg_del = df['delivery_rating'].mean()
        st.markdown(f"""
        <div style="background-color:#ffe9e6;padding:15px;border-radius:10px">
        📦 <b>Delivery Insights:</b><br><br>
        The average delivery rating sits at <b>{avg_del:.2f} stars</b> 🛵, highlighting a generally positive user experience with online orders in Pune.<br><br>
        Unlike dine-in experiences, delivery success depends on multiple factors — packaging quality, punctuality, food temperature, and accurate order fulfillment.<br><br>
        🚀 <i>The smoother KDE curve indicates a majority of ratings fall between 3.5 to 4.5, showing consistency in customer satisfaction — but with scope for improvement.</i><br><br>
        💡 <b>Observation:</b> Restaurants with strong delivery ratings can be flagged as “Reliable for Online Orders,” ideal for working professionals and late-night cravings.<br>
        This data can also help identify outliers — eateries with great food but poor delivery — and strategize improvements accordingly.
        </div>
        """, unsafe_allow_html=True)

if 'Cost (RS)' in df and 'rest_type' in df:
    st.subheader("💰 Average Cost by Restaurant Type (Exploded)")
    rest_df = df[['rest_type', 'Cost (RS)']].dropna()
    rest_df['rest_type'] = rest_df['rest_type'].astype(str).str.split(",")
    rest_df = rest_df.explode('rest_type')
    rest_df['rest_type'] = rest_df['rest_type'].str.strip()
    avg_cost = rest_df.groupby('rest_type')['Cost (RS)'].mean().sort_values(ascending=False).head(10)
    fig4, ax4 = plt.subplots(figsize=figsize)
    sns.barplot(x=avg_cost.values, y=avg_cost.index, ax=ax4, palette="Spectral")
    ax4.set_title("Avg. Cost by Individual Restaurant Type")
    st.pyplot(fig4)
    st.markdown( f"💸 *Observation:* Craving a fancy food experience? Look no further than *{avg_cost.idxmax()}, where an average meal costs around **₹{int(avg_cost.max())}*! 👑🍷\n\n"
    "This chart showcases the *top 10 restaurant types* based on their average cost. It's a great way to spot where premium experiences lie vs budget-friendly options. 🧾\n\n"
    "From quick bites to luxury lounges, this data helps both *diners make better choices* and *restaurateurs identify market positioning*. Whether you're saving or splurging, there’s a spot on this list for every appetite. 💼🍴")

if 'loc' in df:
    st.subheader("📍 Top Locations by Outlet Count")
    loc_count = df['loc'].value_counts().head(10)
    fig5, ax5 = plt.subplots(figsize=figsize)
    sns.barplot(x=loc_count.values, y=loc_count.index, ax=ax5, palette="magma")
    ax5.set_title("Top 10 Locations")
    st.pyplot(fig5)
    top_loc = loc_count.index[0]
    st.markdown(f"📍 *Observation:* Hungry in Pune? Head straight to *{top_loc}—the undisputed food capital with **{loc_count.iloc[0]}+* restaurants sizzling in just that area! 🍽🔥\n\n"
    "This chart reveals the *top 10 foodie hotspots* across the city. Whether you're a casual eater or a gourmet explorer, these locations are *bursting with variety and vibes*. 🌆✨\n\n"
    "Think beyond just quantity—each location represents a unique dining ecosystem. Use this as your *go-to guide for neighborhood food crawls* or business expansion strategies. 📊📍")

if 'cuisine' in df and 'name' in df:
    st.subheader("🍛 Top Restaurants by Selected Cuisine")
    all_cuisines = df['cuisine'].dropna().str.split(",").explode().str.strip().unique()
    selected_cuisine = st.selectbox("Select a Cuisine", sorted(all_cuisines))
    mask = df['cuisine'].str.contains(selected_cuisine, case=False, na=False)
    top_cuisine_df = df[mask].sort_values(by='dine_rating', ascending=False).head(10)
    st.dataframe(top_cuisine_df[['name', 'loc', 'dine_rating', 'Cost (RS)']])

st.subheader("🎛 Filter Restaurants by Cost and Rating")
min_cost, max_cost = int(df['Cost (RS)'].min()), int(df['Cost (RS)'].max())
cost_range = st.slider("Select Cost Range (Rs)", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
rating_range = st.slider("Select Rating Range", 0.0, 5.0, (0.0, 5.0), step=0.1)
filtered_df = df[(df['Cost (RS)'] >= cost_range[0]) & (df['Cost (RS)'] <= cost_range[1]) &
                 (df['dine_rating'].fillna(0) >= rating_range[0]) & (df['dine_rating'].fillna(0) <= rating_range[1])]
st.write(f"Filtered Restaurants: {len(filtered_df)}")
st.dataframe(filtered_df[['rest_name', 'loc', 'dine_rating', 'Cost (RS)']].head(10))

st.subheader("📈 Correlation Heatmap (Rating, Cost, Votes)")
corr_cols = ['dine_rating', 'delivery_rating', 'Cost (RS)', 'votes']
corr_cols = [col for col in corr_cols if col in df.columns]
corr_df = df[corr_cols].dropna()
if not corr_df.empty:
    corr = corr_df.corr()
    fig_corr, ax_corr = plt.subplots(figsize=figsize)
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax_corr)
    st.pyplot(fig_corr)
    st.markdown("🧠 *Observation:* Ever wondered how much your wallet affects your taste buds? 💸🍴\n\n"
    "This heatmap reveals the *hidden relationships* between cost, votes, and ratings. A *strong correlation* between votes and delivery ratings? That means customers love to leave reviews when the delivery rocks! 🚚💬\n\n"
    "Curious patterns may emerge: are costlier places actually better rated, or do affordable joints steal the spotlight? 🔍 Dive into the heatmap to uncover where value and vibes align in Pune’s foodie world!")
else:
        st.info("Not enough data to show correlation heatmap.")

st.subheader("🍛 Cuisine Frequency (Top 15)")
if 'cuisine' in df:
    cuisines_cleaned = df['cuisine'].dropna().str.lower().str.split(",").explode().str.strip()
    cuisines_cleaned = cuisines_cleaned[cuisines_cleaned != ""]
    cuisine_freq = cuisines_cleaned.value_counts().head(15)
    fig_cuisine, ax_cuisine = plt.subplots(figsize=figsize)
    sns.barplot(x=cuisine_freq.values, y=cuisine_freq.index.str.title(), ax=ax_cuisine, palette="Set3")
    ax_cuisine.set_title("Top 15 Cuisines Frequency")
    ax_cuisine.set_xlabel("Count")
    ax_cuisine.set_ylabel("Cuisine")
    st.pyplot(fig_cuisine)
    if not cuisine_freq.empty:
        top_cuisine = cuisine_freq.idxmax().title()
        st.markdown(
        f"🍽 *Observation:* Hungry in Pune? You’re not alone craving *{top_cuisine}* – it’s the undisputed favorite across restaurants! 🔥\n\n"
        "From cozy cafés to luxury diners, this cuisine dominates the city’s culinary scene. Whether you're a local foodie or a visitor, this trend might just help you pick your next meal. "
        "Also, don't miss exploring the other popular cuisines on the chart – Pune's food culture is as diverse as its people! 🌮🍜🍕"
    )
    else:
        st.markdown("Observation: No cuisine data available.")

if 'votes' in df and 'Cost (RS)' in df:
    st.subheader("📊 Votes vs Cost (Popularity vs Expense)")
    fig_scatter, ax_scatter = plt.subplots(figsize=figsize)
    sns.scatterplot(data=df, x='Cost (RS)', y='votes', hue='dine_rating', palette='cool', ax=ax_scatter)
    ax_scatter.set_title("Votes vs Cost")
    st.pyplot(fig_scatter)
    st.markdown(
    "🔎 *Observation:* The scatter reveals an interesting pattern—while some high-cost restaurants receive a flood of votes, many wallet-friendly places also enjoy strong popularity! "
    "Look closely and you'll spot hidden gems: affordable joints with high ratings and loyal customers. 💬💸 "
    "It's not just about price—it's about the experience, flavor, and value! ⭐🍽"
)

st.markdown("---")
st.markdown("## 🚀 Wrapping Up: Your Foodie Footprint in Pune!")
st.balloons()
st.markdown("### 🍽 Your Dashboard Digest")
st.markdown(f"""
- City Explored: Pune 🏙  
- Restaurant Universe: {len(df)} total restaurants  
- Top Cuisine Trend: 🍛 {top_cuisine if 'top_cuisine' in locals() else "Surprise Yourself!"}  
- Hotspot Location: 📍 {top_loc if 'top_loc' in locals() else "Somewhere Delicious"}  
- Spendy Spot: 💸 {avg_cost.idxmax() if 'avg_cost' in locals() else "TBD"} restaurants at Rs. {int(avg_cost.max()) if 'avg_cost' in locals() else "?"} on average  
""")

vibe = st.radio("What's your foodie vibe today?", ["Budget Explorer", "Luxury Feaster", "Hidden Gem Hunter", "Café Hopper"])
recommend = {
    "Budget Explorer": "Check out spots under ₹300 with 4.0+ rating. 💳",
    "Luxury Feaster": "Explore fine-dines with 4.5+ rating and exotic cuisines. 👑",
    "Hidden Gem Hunter": "Sort by rating-to-cost ratio and uncover underrated stars. 🔍",
    "Café Hopper": "Filter for 'Café' types, low cost, cozy locations. ☕"
}
st.success(f"💡 Tip for {vibe}: {recommend[vibe]}")

if st.button("🏱 Reveal a Secret Pune Food Tip"):
    tips = [
        "Try late-night shawarmas in Viman Nagar – surprisingly awesome.",
        "Baner has the quirkiest Asian fusion bistros – hidden in plain sight.",
        "Local thalis in Sadashiv Peth beat any fine-dine on authenticity!",
        "Bakeries in Koregaon Park are a morning delight – try one before 9 AM!"
    ]
    st.info(random.choice(tips))

st.markdown("""
---  
<h3 style='text-align: center;'>Thank you for being a data-savvy foodie! 💡🍕</h3>
<p style='text-align: center;'>May your ratings be high, your bills be low, and your plates always full.</p>
<h1 style='text-align: center;'>🥳 Bon Appétit, Pune! 🥳</h1>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align: center;'>Made with 🧠 + ❤ using Streamlit, Seaborn & a pinch of curiosity.</p>",
    unsafe_allow_html=True
)
