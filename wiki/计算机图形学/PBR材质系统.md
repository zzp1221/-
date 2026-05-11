---
title: "PBR材质系统"
course: 计算机图形学
chapter: 渲染
difficulty: ADVANCED
tags: [图形学, PBR, 材质, BSDF, 渲染]
aliases: [Physically Based Rendering, PBR, BSDF]
source: "Pharr, Jakob & Humphreys《Physically Based Rendering》(PBRT); Disney Principled BRDF 2012; Burley 2015 (PBR in practice)"
updated_at: 2026-05-02
---

## 核心定义

PBR(Physically Based Rendering,基于物理的渲染)遵循物理光学原则模拟光线与材质的交互。核心BRDF(Bidirectional Reflectance Distribution Function)满足三大性质：能量守恒(反射的能量<=入射)、对称性(互换入射出射方向不变)和遵循微面元理论(microfacet theory)。Cook-Torrance microfacets model将表面建模为微小完美镜面的集合(D=法线分布,遮蔽函数G=几何衰减项,F=菲涅尔)。金属与非金属BRDF的区别——金属无diffuse分量(所有反射都是镜面)。

## Disney Principled BSDF

Disney的Principled BRDF(2012)将复杂的物理参数简化为艺术友好的参数集：baseColor(基础色)、metallic(金属度0-1)、roughness(粗糙度)、specular/specularTint、sheen、clearcoat(清漆层)、transmission。此模型不是物理完美的但它为艺术创作提供直觉控制同时保持物理合理的外观。GGX(Trowbridge-Reitz)是当今最常用的microfacet法线分布——比旧的Beckmann分布有更长的尾部(soft highlights + long tail——更自然)。Image-based lighting(IBL——用环境贴图hdr cubemap做光照)通过预计算辐照度和预过滤环境贴图加速。

## 关键结论

1. PBR的diffuse+specular归一化保证能量守恒——材质不生成额外的光 2. 菲涅尔效应的直观表现—— grazing angle (glancing) 下几乎所有表面变镜面 3. Standard metallic workflow(多数的game engine采用)使用roughness/metallic贴图 4. ASTC/BC压缩贴图在运行时解压——多个贴图打包进不同channel(Packed textures/optimize usage) 5. RTX and ReSTIR enable real-time PBR path-tracing(光子路径采样——降噪器denoiser提供低样本count)

## 关联知识点

[[计算机图形学-光线追踪与光栅化]] [[计算机图形学-全局光照与辐射度]] [[计算机组成原理-GPU渲染管线与GPGPU]]
