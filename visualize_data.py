import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import Counter
from datetime import datetime
import re
import warnings

warnings.filterwarnings('ignore')

# Set style for better-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class HackathonVisualizer:
    """Generate insightful visualizations from hackathon data"""

    def __init__(self, json_file='remote_hackathons.json'):
        """Load and prepare data"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.hackathons = json.load(f)
        self.df = self._prepare_dataframe()

    def _prepare_dataframe(self):
        """Convert hackathons to pandas DataFrame"""
        data = []
        for h in self.hackathons:
            row = {
                'title': h.get('title', ''),
                'status': h.get('status', 'Unknown'),
                'location_type': h.get('location_type', 'Unknown'),
                'dates': h.get('dates', ''),
                'location': h.get('location', ''),
                'themes': h.get('themes', []),
                'num_themes': len(h.get('themes', [])),
            }

            # Extract year from dates
            dates_str = h.get('dates', '')
            year_match = re.search(r'20\d{2}', dates_str)
            if year_match:
                row['year'] = int(year_match.group())
            else:
                row['year'] = None

            # Extract month
            months = {
                'Jan': 1, 'Feb': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                'July': 7, 'Aug': 8, 'Sept': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            for month_name, month_num in months.items():
                if month_name in dates_str:
                    row['month'] = month_num
                    row['month_name'] = month_name
                    break
            else:
                row['month'] = None
                row['month_name'] = 'Unknown'

            data.append(row)

        return pd.DataFrame(data)

    def generate_all_visualizations(self, output_dir='charts'):
        """Generate all visualizations and return insights"""
        insights = {
            'total_hackathons': len(self.hackathons),
            'charts_generated': []
        }

        print("Generating visualizations...")

        # 1. Theme Popularity
        print("  1. Theme popularity chart...")
        insights['top_themes'] = self._plot_theme_popularity(output_dir)
        insights['charts_generated'].append('01_theme_popularity.png')

        # 2. Yearly Trends
        print("  2. Yearly trends chart...")
        insights['yearly_trends'] = self._plot_yearly_trends(output_dir)
        insights['charts_generated'].append('02_yearly_trends.png')

        # 3. Monthly Distribution
        print("  3. Monthly distribution chart...")
        insights['peak_months'] = self._plot_monthly_distribution(output_dir)
        insights['charts_generated'].append('03_monthly_distribution.png')

        # 4. Geographic Distribution
        print("  4. Geographic distribution chart...")
        insights['geographic_insights'] = self._plot_geographic_distribution(output_dir)
        insights['charts_generated'].append('04_geographic_distribution.png')

        # 5. Theme Combinations
        print("  5. Theme combinations chart...")
        insights['theme_combinations'] = self._plot_theme_combinations(output_dir)
        insights['charts_generated'].append('05_theme_combinations.png')

        # 6. Comprehensive Dashboard
        print("  6. Comprehensive dashboard...")
        self._plot_dashboard(output_dir)
        insights['charts_generated'].append('06_dashboard.png')

        print(f"\nAll visualizations saved to '{output_dir}/' directory")
        return insights

    def _plot_theme_popularity(self, output_dir):
        """Plot theme popularity"""
        theme_counter = Counter()
        for h in self.hackathons:
            for theme in h.get('themes', []):
                theme_counter[theme] += 1

        top_themes = theme_counter.most_common(15)
        themes, counts = zip(*top_themes)

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(range(len(themes)), counts, color=sns.color_palette("viridis", len(themes)))
        ax.set_yticks(range(len(themes)))
        ax.set_yticklabels(themes)
        ax.set_xlabel('Number of Hackathons', fontsize=12, fontweight='bold')
        ax.set_title('Top 15 Most Popular Hackathon Themes', fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax.text(count + 0.3, i, str(count), va='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/01_theme_popularity.png', dpi=300, bbox_inches='tight')
        plt.close()

        return dict(top_themes[:5])

    def _plot_yearly_trends(self, output_dir):
        """Plot yearly trends"""
        yearly_data = self.df[self.df['year'].notna()].groupby('year').size()

        fig, ax = plt.subplots(figsize=(12, 6))
        years = yearly_data.index
        counts = yearly_data.values

        ax.plot(years, counts, marker='o', linewidth=2.5, markersize=10, color='#2E86AB')
        ax.fill_between(years, counts, alpha=0.3, color='#2E86AB')

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Hackathons', fontsize=12, fontweight='bold')
        ax.set_title('Hackathon Trends Over Time', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)

        # Add value labels
        for year, count in zip(years, counts):
            ax.text(year, count + 1, str(count), ha='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/02_yearly_trends.png', dpi=300, bbox_inches='tight')
        plt.close()

        peak_year = int(yearly_data.idxmax())
        return {
            'peak_year': peak_year,
            'peak_count': int(yearly_data.max()),
            'trend': 'growing' if counts[-1] > counts[0] else 'declining'
        }

    def _plot_monthly_distribution(self, output_dir):
        """Plot monthly distribution"""
        monthly_data = self.df[self.df['month'].notna()].groupby('month_name').size()

        # Order by month
        month_order = ['Jan', 'Feb', 'March', 'April', 'May', 'June',
                       'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
        monthly_data = monthly_data.reindex([m for m in month_order if m in monthly_data.index])

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(monthly_data)), monthly_data.values,
                      color=sns.color_palette("coolwarm", len(monthly_data)))
        ax.set_xticks(range(len(monthly_data)))
        ax.set_xticklabels(monthly_data.index, rotation=45, ha='right')
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Hackathons', fontsize=12, fontweight='bold')
        ax.set_title('Hackathon Distribution by Month', fontsize=14, fontweight='bold', pad=20)

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, monthly_data.values)):
            ax.text(i, count + 0.3, str(count), ha='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/03_monthly_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        peak_month = monthly_data.idxmax()
        return {
            'peak_month': peak_month,
            'peak_count': int(monthly_data.max()),
            'slowest_month': monthly_data.idxmin()
        }

    def _plot_geographic_distribution(self, output_dir):
        """Plot geographic distribution and online vs in-person split"""
        # Analyze locations
        online_count = 0
        in_person_count = 0
        countries = Counter()
        cities = Counter()

        for h in self.hackathons:
            location = h.get('location', '').strip()

            if location.lower() == 'online':
                online_count += 1
            elif location.lower() == 'in-person' or location:
                in_person_count += 1
                # Extract country/city info
                if location.lower() != 'in-person':
                    parts = [p.strip() for p in location.split(',')]
                    if len(parts) >= 2:
                        country = parts[-1]
                        city = parts[0]
                        countries[country] += 1
                        cities[city] += 1
                    elif len(parts) == 1:
                        countries[parts[0]] += 1

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Online vs In-Person Pie Chart
        format_data = [online_count, in_person_count]
        format_labels = ['Online', 'In-Person']
        colors1 = ['#2E86AB', '#A23B72']
        wedges, texts, autotexts = ax1.pie(
            format_data,
            labels=format_labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors1,
            textprops={'fontweight': 'bold', 'fontsize': 12}
        )
        ax1.set_title('Online vs In-Person Distribution', fontsize=14, fontweight='bold', pad=20)

        # 2. Top Countries
        top_countries = countries.most_common(10)
        if top_countries:
            country_names, country_counts = zip(*top_countries)
            bars = ax2.barh(range(len(country_names)), country_counts,
                           color=sns.color_palette("viridis", len(country_names)))
            ax2.set_yticks(range(len(country_names)))
            ax2.set_yticklabels(country_names)
            ax2.set_xlabel('Number of Hackathons', fontsize=10, fontweight='bold')
            ax2.set_title('Top 10 Countries', fontsize=14, fontweight='bold', pad=20)
            ax2.invert_yaxis()
            for i, count in enumerate(country_counts):
                ax2.text(count + 0.1, i, str(count), va='center', fontsize=9, fontweight='bold')

        # 3. Top Cities
        top_cities = cities.most_common(10)
        if top_cities:
            city_names, city_counts = zip(*top_cities)
            bars = ax3.barh(range(len(city_names)), city_counts,
                           color=sns.color_palette("mako", len(city_names)))
            ax3.set_yticks(range(len(city_names)))
            ax3.set_yticklabels(city_names, fontsize=9)
            ax3.set_xlabel('Number of Hackathons', fontsize=10, fontweight='bold')
            ax3.set_title('Top 10 Cities', fontsize=14, fontweight='bold', pad=20)
            ax3.invert_yaxis()
            for i, count in enumerate(city_counts):
                ax3.text(count + 0.1, i, str(count), va='center', fontsize=9, fontweight='bold')

        # 4. Format Distribution Stats
        ax4.axis('off')
        stats_text = f"""
        GLOBAL REACH STATISTICS

        Total Hackathons: {len(self.hackathons)}

        Format Split:
        • Online: {online_count} ({online_count/len(self.hackathons)*100:.1f}%)
        • In-Person: {in_person_count} ({in_person_count/len(self.hackathons)*100:.1f}%)

        Geographic Coverage:
        • Countries: {len(countries)}
        • Cities: {len(cities)}

        Accessibility:
        {'🌍 Global reach via online format' if online_count > in_person_count else '🏢 Primarily in-person events'}
        """
        ax4.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout()
        plt.savefig(f'{output_dir}/04_geographic_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        return {
            'online_count': online_count,
            'in_person_count': in_person_count,
            'online_percentage': round(online_count/len(self.hackathons)*100, 1),
            'countries': len(countries),
            'cities': len(cities),
            'top_country': countries.most_common(1)[0] if countries else ('Unknown', 0)
        }

    def _plot_theme_combinations(self, output_dir):
        """Plot theme combinations"""
        # Find most common theme pairs
        theme_pairs = Counter()
        for h in self.hackathons:
            themes = h.get('themes', [])
            if len(themes) >= 2:
                for i in range(len(themes)):
                    for j in range(i + 1, len(themes)):
                        pair = tuple(sorted([themes[i], themes[j]]))
                        theme_pairs[pair] += 1

        top_pairs = theme_pairs.most_common(10)

        if not top_pairs:
            # No pairs found, skip
            return {}

        fig, ax = plt.subplots(figsize=(12, 6))
        pair_labels = [f"{p[0]} + {p[1]}" for p, _ in top_pairs]
        counts = [count for _, count in top_pairs]

        bars = ax.barh(range(len(pair_labels)), counts,
                       color=sns.color_palette("mako", len(pair_labels)))
        ax.set_yticks(range(len(pair_labels)))
        ax.set_yticklabels(pair_labels, fontsize=9)
        ax.set_xlabel('Number of Hackathons', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 Theme Combinations', fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax.text(count + 0.1, i, str(count), va='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/05_theme_combinations.png', dpi=300, bbox_inches='tight')
        plt.close()

        return {str(pair): count for pair, count in top_pairs[:3]}

    def _plot_dashboard(self, output_dir):
        """Create a comprehensive dashboard"""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. Total Hackathons (Big Number)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.text(0.5, 0.5, str(len(self.hackathons)),
                ha='center', va='center', fontsize=60, fontweight='bold', color='#2E86AB')
        ax1.text(0.5, 0.2, 'Total Hackathons',
                ha='center', va='center', fontsize=14, color='gray')
        ax1.axis('off')

        # 2. Unique Themes
        ax2 = fig.add_subplot(gs[0, 1])
        all_themes = set()
        for h in self.hackathons:
            all_themes.update(h.get('themes', []))
        ax2.text(0.5, 0.5, str(len(all_themes)),
                ha='center', va='center', fontsize=60, fontweight='bold', color='#A23B72')
        ax2.text(0.5, 0.2, 'Unique Themes',
                ha='center', va='center', fontsize=14, color='gray')
        ax2.axis('off')

        # 3. Average Themes per Hackathon
        ax3 = fig.add_subplot(gs[0, 2])
        avg_themes = self.df['num_themes'].mean()
        ax3.text(0.5, 0.5, f"{avg_themes:.1f}",
                ha='center', va='center', fontsize=60, fontweight='bold', color='#F18F01')
        ax3.text(0.5, 0.2, 'Avg Themes/Hackathon',
                ha='center', va='center', fontsize=14, color='gray')
        ax3.axis('off')

        # 4. Top 10 Themes
        ax4 = fig.add_subplot(gs[1, :])
        theme_counter = Counter()
        for h in self.hackathons:
            for theme in h.get('themes', []):
                theme_counter[theme] += 1
        top_10_themes = theme_counter.most_common(10)
        themes, counts = zip(*top_10_themes)
        bars = ax4.bar(range(len(themes)), counts, color=sns.color_palette("viridis", len(themes)))
        ax4.set_xticks(range(len(themes)))
        ax4.set_xticklabels(themes, rotation=45, ha='right')
        ax4.set_ylabel('Count', fontweight='bold')
        ax4.set_title('Top 10 Themes', fontweight='bold', fontsize=12)
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax4.text(i, count + 0.3, str(count), ha='center', fontsize=9, fontweight='bold')

        # 5. Yearly Trends
        ax5 = fig.add_subplot(gs[2, :2])
        yearly_data = self.df[self.df['year'].notna()].groupby('year').size()
        ax5.plot(yearly_data.index, yearly_data.values, marker='o',
                linewidth=2.5, markersize=8, color='#2E86AB')
        ax5.fill_between(yearly_data.index, yearly_data.values, alpha=0.3, color='#2E86AB')
        ax5.set_xlabel('Year', fontweight='bold')
        ax5.set_ylabel('Count', fontweight='bold')
        ax5.set_title('Yearly Trends', fontweight='bold', fontsize=12)
        ax5.grid(True, alpha=0.3)

        # 6. Online vs In-Person Split
        ax6 = fig.add_subplot(gs[2, 2])
        online_count = 0
        in_person_count = 0
        for h in self.hackathons:
            location = h.get('location', '').strip().lower()
            if location == 'online':
                online_count += 1
            elif location:
                in_person_count += 1

        if online_count + in_person_count > 0:
            colors = ['#2E86AB', '#A23B72']
            wedges, texts, autotexts = ax6.pie(
                [online_count, in_person_count],
                labels=['Online', 'In-Person'],
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'fontsize': 9, 'fontweight': 'bold'}
            )
        ax6.set_title('Format Distribution', fontweight='bold', fontsize=12)

        fig.suptitle('Hackathon Data Dashboard', fontsize=18, fontweight='bold', y=0.98)
        plt.savefig(f'{output_dir}/06_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()

    def generate_insights_report(self, insights):
        """Generate a text report of insights"""
        report = []
        report.append("=" * 70)
        report.append("HACKATHON DATA INSIGHTS REPORT")
        report.append("=" * 70)
        report.append("")

        report.append(f"📊 Total Hackathons Analyzed: {insights['total_hackathons']}")
        report.append("")

        report.append("🏆 TOP THEMES")
        report.append("-" * 70)
        for i, (theme, count) in enumerate(insights['top_themes'].items(), 1):
            report.append(f"  {i}. {theme.title()}: {count} hackathons")
        report.append("")

        if 'yearly_trends' in insights:
            trends = insights['yearly_trends']
            report.append("📈 YEARLY TRENDS")
            report.append("-" * 70)
            report.append(f"  Peak Year: {trends['peak_year']} ({trends['peak_count']} hackathons)")
            report.append(f"  Overall Trend: {trends['trend'].title()}")
            report.append("")

        if 'peak_months' in insights:
            monthly = insights['peak_months']
            report.append("📅 SEASONAL PATTERNS")
            report.append("-" * 70)
            report.append(f"  Busiest Month: {monthly['peak_month']} ({monthly['peak_count']} hackathons)")
            report.append(f"  Slowest Month: {monthly['slowest_month']}")
            report.append("")

        if 'geographic_insights' in insights:
            geo = insights['geographic_insights']
            report.append("🌍 GEOGRAPHIC DISTRIBUTION")
            report.append("-" * 70)
            report.append(f"  Online: {geo['online_count']} ({geo['online_percentage']}%)")
            report.append(f"  In-Person: {geo['in_person_count']}")
            report.append(f"  Countries Represented: {geo['countries']}")
            report.append(f"  Cities Represented: {geo['cities']}")
            report.append("")

        report.append("💡 KEY INSIGHTS")
        report.append("-" * 70)
        report.append(self._generate_key_insights(insights))
        report.append("")

        report.append("📁 Generated Charts:")
        report.append("-" * 70)
        for chart in insights['charts_generated']:
            report.append(f"  ✓ {chart}")
        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def _generate_key_insights(self, insights):
        """Generate key insights based on data"""
        insights_text = []

        # Theme insights
        top_theme = list(insights['top_themes'].keys())[0]
        insights_text.append(f"  1. '{top_theme.title()}' is the most popular theme, appearing in")
        insights_text.append(f"     {insights['top_themes'][top_theme]} hackathons.")

        # Temporal insights
        if 'yearly_trends' in insights:
            trends = insights['yearly_trends']
            insights_text.append(f"  2. Hackathon activity peaked in {trends['peak_year']}, showing")
            insights_text.append(f"     a {trends['trend']} trend overall.")

        # Seasonal insights
        if 'peak_months' in insights:
            monthly = insights['peak_months']
            insights_text.append(f"  3. {monthly['peak_month']} is the busiest month for hackathons,")
            insights_text.append(f"     while {monthly['slowest_month']} sees the least activity.")

        # Geographic insights
        if 'geographic_insights' in insights:
            geo = insights['geographic_insights']
            insights_text.append(f"  4. {geo['online_percentage']}% of hackathons are online, spanning")
            insights_text.append(f"     {geo['countries']} countries and increasing global accessibility.")

        return "\n".join(insights_text)


def main():
    """Main function"""
    print("=" * 70)
    print("HACKATHON DATA VISUALIZATION")
    print("=" * 70)
    print()

    # Create visualizer
    viz = HackathonVisualizer('remote_hackathons.json')

    # Generate all visualizations
    insights = viz.generate_all_visualizations('charts')

    # Generate and print insights report
    print()
    report = viz.generate_insights_report(insights)
    print(report)

    # Save report to file
    with open('charts/insights_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    print("✓ Insights report saved to 'charts/insights_report.txt'")


if __name__ == "__main__":
    main()
