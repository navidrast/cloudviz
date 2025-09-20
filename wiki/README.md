# CloudViz Wiki

This directory contains the complete CloudViz documentation wiki. The wiki provides comprehensive guides, tutorials, and reference materials for using CloudViz in production environments.

## 📖 Wiki Contents

### Core Documentation
- **[Home](Home.md)** - Project overview and main navigation hub
- **[Getting Started](Getting-Started.md)** - Installation and quick start guide
- **[API Documentation](API-Documentation.md)** - Complete REST API reference
- **[Architecture](Architecture.md)** - System design and technical architecture
- **[Configuration](Configuration.md)** - Environment and YAML configuration

### Cloud Provider Integration  
- **[Cloud Providers](Cloud-Providers.md)** - Azure, AWS, GCP setup and usage
- **[Visualization](Visualization.md)** - Diagram generation, themes, and export

### Automation & Deployment
- **[n8n Integration](n8n-Integration.md)** - Workflow automation and examples
- **[Deployment](Deployment.md)** - Docker, Kubernetes, production deployment

### Development & Support
- **[Development](Development.md)** - Contributing and development environment
- **[Troubleshooting](Troubleshooting.md)** - Common issues and solutions
- **[Examples](Examples.md)** - Real-world use cases and integrations

### Navigation
- **[_Navigation](_Navigation.md)** - Complete navigation index and quick reference

## 🚀 Using This Wiki

### For GitHub Wiki
These files are designed to be imported into GitHub's wiki system:

1. **Enable GitHub Wiki** for your repository
2. **Clone the wiki repository**:
   ```bash
   git clone https://github.com/navidrast/cloudviz.wiki.git
   ```
3. **Copy wiki files**:
   ```bash
   cp -r wiki/* cloudviz.wiki/
   cd cloudviz.wiki
   git add .
   git commit -m "Add comprehensive CloudViz wiki"
   git push origin master
   ```

### For Local Documentation
You can also use these files as local documentation:

1. **View with any Markdown viewer**
2. **Serve with Python**:
   ```bash
   cd wiki
   python -m http.server 8080
   # Then use a markdown viewer at http://localhost:8080
   ```
3. **Convert to static site** with tools like:
   - [MkDocs](https://www.mkdocs.org/)
   - [GitBook](https://www.gitbook.com/)
   - [Docusaurus](https://docusaurus.io/)

### For Documentation Sites

#### MkDocs Setup
```yaml
# mkdocs.yml
site_name: CloudViz Documentation
nav:
  - Home: Home.md
  - Getting Started: Getting-Started.md
  - API Documentation: API-Documentation.md
  - Architecture: Architecture.md
  - Cloud Providers: Cloud-Providers.md
  - Visualization: Visualization.md
  - n8n Integration: n8n-Integration.md
  - Deployment: Deployment.md
  - Configuration: Configuration.md
  - Troubleshooting: Troubleshooting.md
  - Development: Development.md
  - Examples: Examples.md

theme:
  name: material
  features:
    - navigation.sections
    - navigation.top
    - search.highlight
```

#### GitBook Setup
```json
{
  "title": "CloudViz Documentation",
  "description": "Enterprise Multi-Cloud Infrastructure Visualization",
  "structure": {
    "readme": "Home.md",
    "summary": "_Navigation.md"
  }
}
```

## 📊 Wiki Statistics

- **Total Pages**: 12 comprehensive guides
- **Total Content**: ~200,000 words
- **Coverage**: Complete end-to-end documentation
- **Examples**: 50+ code examples and configuration samples
- **Diagrams**: 30+ Mermaid diagrams and flowcharts

## 🔄 Maintenance

### Updating the Wiki
When updating CloudViz features, ensure corresponding wiki updates:

1. **API changes** → Update [API Documentation](API-Documentation.md)
2. **New features** → Update [Getting Started](Getting-Started.md) and [Examples](Examples.md)
3. **Configuration changes** → Update [Configuration](Configuration.md)
4. **New cloud providers** → Update [Cloud Providers](Cloud-Providers.md)
5. **Deployment changes** → Update [Deployment](Deployment.md)

### Content Guidelines
- **Keep examples current** with latest CloudViz version
- **Test all code examples** before publishing
- **Update screenshots** when UI changes
- **Cross-reference pages** for better navigation
- **Include version information** for breaking changes

### Quality Checklist
- [ ] All code examples tested and working
- [ ] Screenshots are current and clear
- [ ] Internal links work correctly
- [ ] External links are valid
- [ ] Content is well-organized and logical
- [ ] Spelling and grammar checked
- [ ] Consistent formatting and style

## 🎯 Key Features

### Comprehensive Coverage
- **Installation** to **Production Deployment**
- **Basic Usage** to **Advanced Integrations**
- **Single Cloud** to **Multi-Cloud Scenarios**
- **Manual Operations** to **Full Automation**

### Rich Examples
- **Real-world use cases** across industries
- **Complete configuration samples**
- **Working code examples**
- **Integration patterns**
- **Troubleshooting scenarios**

### Multiple Formats
- **Markdown** for easy reading and editing
- **Mermaid diagrams** for visual explanation
- **Code blocks** with syntax highlighting
- **Tables** for quick reference
- **Screenshots** for UI guidance

### Navigation Aids
- **Cross-references** between related topics
- **Quick start paths** for common tasks
- **Troubleshooting guides** for issues
- **API reference** with examples
- **Configuration templates** for different scenarios

## 🛠️ Tools and Scripts

### Generate Table of Contents
```bash
# Generate TOC for each markdown file
find . -name "*.md" -exec gh-md-toc {} \;
```

### Check Links
```bash
# Check all markdown links
markdown-link-check *.md
```

### Convert to Other Formats
```bash
# Convert to HTML
pandoc Home.md -o Home.html

# Convert to PDF
pandoc *.md -o CloudViz-Documentation.pdf

# Convert to Word
pandoc *.md -o CloudViz-Documentation.docx
```

### Generate Site
```bash
# Using MkDocs
mkdocs build
mkdocs serve

# Using GitBook
gitbook build
gitbook serve
```

## 🤝 Contributing

### Documentation Contributions
1. **Fork the repository**
2. **Create a feature branch** for documentation updates
3. **Make changes** following the style guide
4. **Test all examples** and links
5. **Submit a pull request**

### Style Guide
- Use **clear, concise language**
- Include **working examples** for all features
- **Cross-reference** related topics
- Use **consistent formatting**
- Include **troubleshooting information**

### Review Process
- **Technical accuracy** review
- **Content clarity** review  
- **Link validation** check
- **Example testing** verification
- **Style consistency** check

---

This wiki provides everything needed to successfully deploy, configure, and use CloudViz in enterprise environments. For questions or improvements, please contribute via GitHub issues or pull requests.