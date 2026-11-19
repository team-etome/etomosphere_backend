import openpyxl
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from app1.models import Solution
from products.models import (
    Category, CategoryImage,
    CatalogueProduct, CatalogueProductImage,
    Brand, Variant, VariantImage,
)

EXCEL_PATH = r'C:\Users\LeGiON\Downloads\Etome_Product_Bible_Filled.xlsx'


class Command(BaseCommand):
    help = 'Clear all products and import from Etome_Product_Bible_Filled.xlsx'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('── Clearing existing data ──')
            self._clear()

            self.stdout.write('── Importing from Excel ──')
            stats = self._import()

        self.stdout.write(self.style.SUCCESS(
            f'\nDone!  {stats["solutions"]} solutions · '
            f'{stats["products"]} catalogue products · '
            f'{stats["brands"]} brands · '
            f'{stats["variants"]} variants'
        ))

    # ──────────────────────────────────────────────────────────
    def _clear(self):
        VariantImage.objects.all().delete()
        CatalogueProductImage.objects.all().delete()
        CategoryImage.objects.all().delete()
        Variant.objects.all().delete()
        Brand.objects.all().delete()
        CatalogueProduct.objects.all().delete()
        Category.objects.all().delete()
        Solution.objects.all().delete()
        self.stdout.write(self.style.WARNING('  All product data cleared.'))

    # ──────────────────────────────────────────────────────────
    def _import(self):
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb['Master Product Database']
        rows = list(ws.iter_rows(min_row=2, values_only=True))

        # ── forward-fill state ──
        cur_vertical = cur_cat_name = cur_type = cur_brand = None
        cur_industry = cur_application = cur_features = cur_usp = cur_desc = None

        # ── caches to avoid redundant DB hits ──
        solution_cache = {}           # vertical_name -> Solution
        category_cache = {}           # (solution_id, type_slug) -> Category
        cp_cache = {}                 # (category_id, cp_slug) -> CatalogueProduct
        brand_cache = {}              # brand_name -> Brand
        brand_cp_links = set()        # (brand_id, cp_id) already linked

        sol_order = 0
        cat_order = {}   # solution_id -> int
        cp_order = {}    # category_id -> int
        variant_count = 0

        for raw in rows:
                cf, vertical, brand_name, model, size, cat_col, type_col, \
                    industry, application, features, usp, desc, warranty, remarks = raw

                # skip blank rows
                if not any([vertical, brand_name, model, cat_col]):
                    continue

                # forward-fill
                if vertical:    cur_vertical  = vertical.strip()
                if cat_col:     cur_cat_name  = cat_col.strip()
                if type_col:    cur_type      = type_col.strip()
                if brand_name:  cur_brand     = brand_name.strip()
                if industry:    cur_industry  = industry
                if application: cur_application = application
                if features:    cur_features  = features
                if usp:         cur_usp       = usp
                if desc:        cur_desc      = desc

                # rows without a model are just filling context
                if model is None:
                    continue
                model = str(model).strip()
                if not model:
                    continue

                # ── Solution ──────────────────────────────────
                if cur_vertical not in solution_cache:
                    sol_order += 1
                    sol, created = Solution.objects.get_or_create(
                        slug=slugify(cur_vertical),
                        defaults={'name': cur_vertical, 'sort_order': sol_order},
                    )
                    solution_cache[cur_vertical] = sol
                    self.stdout.write(f'  [Solution] {cur_vertical}')
                solution = solution_cache[cur_vertical]

                # ── Category (keyed by Solution + Type) ───────
                type_label = cur_type or 'Hardware'
                cat_key = (solution.id, slugify(type_label))
                if cat_key not in category_cache:
                    cat_slug = f"{slugify(cur_vertical)}-{slugify(type_label)}"
                    order = cat_order.get(solution.id, 0) + 1
                    cat_order[solution.id] = order
                    cat, _ = Category.objects.get_or_create(
                        slug=cat_slug,
                        defaults={
                            'solution': solution,
                            'name': type_label,
                            'sort_order': order,
                        },
                    )
                    category_cache[cat_key] = cat
                category = category_cache[cat_key]

                # ── CatalogueProduct (keyed by Category + product name) ─
                cp_name = cur_cat_name or cur_vertical
                cp_slug = f"{slugify(cur_vertical)}-{slugify(cp_name)}"
                cp_key = (category.id, cp_slug)
                if cp_key not in cp_cache:
                    order = cp_order.get(category.id, 0) + 1
                    cp_order[category.id] = order
                    cp, _ = CatalogueProduct.objects.get_or_create(
                        slug=cp_slug,
                        defaults={
                            'category': category,
                            'name': cp_name,
                            'description': cur_desc or '',
                            'sort_order': order,
                        },
                    )
                    cp_cache[cp_key] = cp
                    self.stdout.write(f'    [Product] {cp_name}')
                catalogue_product = cp_cache[cp_key]

                # ── Brand ─────────────────────────────────────
                brand_label = cur_brand or 'OEM'
                if brand_label not in brand_cache:
                    brand, _ = Brand.objects.get_or_create(name=brand_label)
                    brand_cache[brand_label] = brand
                brand = brand_cache[brand_label]

                # link brand ↔ catalogue_product (M2M)
                link_key = (brand.id, catalogue_product.id)
                if link_key not in brand_cp_links:
                    brand.products.add(catalogue_product)
                    brand_cp_links.add(link_key)

                # ── Variant ───────────────────────────────────
                size_str = size.strip() if size and str(size).strip() else ''
                if size_str and size_str not in model:
                    variant_name = f"{model} ({size_str})"
                else:
                    variant_name = model

                spec = {}
                if size_str:               spec['size']            = size_str
                if cur_industry:           spec['target_industry'] = cur_industry
                if cur_application:        spec['application']     = cur_application
                if cur_features:           spec['key_features']    = cur_features
                if warranty:               spec['warranty']        = str(warranty)
                if remarks:                spec['remarks']         = str(remarks)

                Variant.objects.create(
                    brand=brand,
                    catalogue_product=catalogue_product,
                    name=variant_name,
                    description=cur_usp or '',
                    spec_json=spec,
                    stock_status='in_stock',
                    lifecycle_status='active',
                )
                variant_count += 1
                self.stdout.write(f'      [Variant] {variant_name}')

        return {
            'solutions': len(solution_cache),
            'products':  len(cp_cache),
            'brands':    len(brand_cache),
            'variants':  variant_count,
        }
