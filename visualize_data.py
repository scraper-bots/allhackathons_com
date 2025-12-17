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

        # 4. Location Type Distribution
        print("  4. Location type chart...")
        insights['location_insights'] = self._plot_location_types(output_dir)
        insights['charts_generated'].append('04_location_types.png')

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

    def _plot_location_types(self, output_dir):
        """Plot location type distribution"""
        # Count location types from original data (more accurate)
        location_counter = Counter()
        for h in self.hackathons:
            loc_type = h.get('location_type', 'Unknown')
            if loc_type:
                location_counter[loc_type] += 1

        if not location_counter:
            location_counter['Unknown'] = len(self.hackathons)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Pie chart
        colors = sns.color_palette("Set2", len(location_counter))
        wedges, texts, autotexts = ax1.pie(
            location_counter.values(),
            labels=location_counter.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontweight': 'bold', 'fontsize': 11}
        )
        ax1.set_title('Hackathon Location Types', fontsize=14, fontweight='bold', pad=20)

        # Bar chart
        bars = ax2.bar(range(len(location_counter)), location_counter.values(), color=colors)
        ax2.set_xticks(range(len(location_counter)))
        ax2.set_xticklabels(location_counter.keys(), rotation=45, ha='right')
        ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax2.set_title('Location Type Distribution', fontsize=14, fontweight='bold', pad=20)

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, location_counter.values())):
            ax2.text(i, count + 0.5, str(count), ha='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/04_location_types.png', dpi=300, bbox_inches='tight')
        plt.close()

        return dict(location_counter)

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

        # 6. Location Types
        ax6 = fig.add_subplot(gs[2, 2])
        location_counter = Counter()
        for h in self.hackathons:
            loc_type = h.get('location_type', 'Unknown')
            if loc_type:
                location_counter[loc_type] += 1
        if not location_counter:
            location_counter['Unknown'] = len(self.hackathons)
        colors = sns.color_palette("Set2", len(location_counter))
        wedges, texts, autotexts = ax6.pie(
            location_counter.values(),
            labels=location_counter.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 9, 'fontweight': 'bold'}
        )
        ax6.set_title('Location Types', fontweight='bold', fontsize=12)

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

        if 'location_insights' in insights:
            report.append("🌍 LOCATION DISTRIBUTION")
            report.append("-" * 70)
            for loc_type, count in insights['location_insights'].items():
                percentage = (count / insights['total_hackathons']) * 100
                report.append(f"  {loc_type}: {count} ({percentage:.1f}%)")
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

        # Location insights
        if 'location_insights' in insights:
            online_count = insights['location_insights'].get('ONLINE', 0)
            total = insights['total_hackathons']
            if online_count > 0:
                online_pct = (online_count / total) * 100
                insights_text.append(f"  4. Online hackathons make up {online_pct:.1f}% of events,")
                insights_text.append(f"     increasing accessibility for global participants.")

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
